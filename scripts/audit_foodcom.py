"""Reproducible local data checks, not preprocessing approval or model training."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import random
import re
import urllib.error
import urllib.parse
import urllib.request

import pyarrow
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data/raw/foodcom-v2"
OUT = ROOT / "data/processed/foodcom-v2"
SEED = 20260930


def canonical_id(value):
    """Source recipe IDs are floats; reject rather than truncate invalid IDs."""
    if value is None or isinstance(value, bool):
        return None
    try:
        numeric = float(value)
        return int(numeric) if math.isfinite(numeric) and numeric > 0 and numeric.is_integer() else None
    except (ValueError, TypeError, OverflowError):
        return None


def has_text(value):
    return isinstance(value, str) and bool(value.strip())


def usable_list(value):
    return bool(value) and all(has_text(item) for item in value)


def duration_minutes(value):
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", value)
    if not match or not any(match.groups()):
        return None
    hours, minutes, seconds = (int(part or 0) for part in match.groups())
    return hours * 60 + minutes + seconds / 60


def probe_photo(item):
    url = item["Images"][0]
    parsed = urllib.parse.urlsplit(url)
    result = {"recipe_id": canonical_id(item["RecipeId"]), "name": item["Name"], "url": url}
    # Do not fetch arbitrary addresses supplied by a third-party dataset.
    if parsed.scheme != "https" or parsed.hostname != "img.sndimg.com" or parsed.port not in (None, 443):
        return result | {"ok": False, "reason": "not_allowlisted"}
    try:
        request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Tasteprint-local-data-audit/1.0"})
        # No redirects: a redirect is a result to review, not a fetch of an unknown host.
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        with urllib.request.build_opener(NoRedirect).open(request, timeout=15) as response:
            mime = response.headers.get("Content-Type", "").split(";")[0]
            return result | {"status": response.status, "content_type": mime,
                             "ok": response.status == 200 and mime.startswith("image/")}
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        return result | {"ok": False, "reason": type(error).__name__,
                         "status": getattr(error, "code", None)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-images", type=int, default=0, choices=range(0, 25))
    parser.add_argument("--photos-only", action="store_true", help="Probe the existing draft without repeating the full-file audit")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.photos_only:
        if not args.check_images:
            parser.error("--photos-only requires --check-images")
        output = json.loads((OUT / "audit.json").read_text(encoding="utf-8"))
        selected = json.loads((OUT / "catalog-review-draft.json").read_text(encoding="utf-8"))
        current_manifest = json.loads((RAW / "manifest.json").read_text(encoding="utf-8"))
        if output["source_manifest"] != current_manifest:
            raise ValueError("Audit and current download provenance differ; rerun the full audit")
        with ThreadPoolExecutor(max_workers=4) as executor:
            output["photo_checks"] = list(executor.map(probe_photo, selected[:args.check_images]))
        output["photo_checked_at_utc"] = datetime.now(timezone.utc).isoformat()
        (OUT / "audit-with-photo-checks.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"photos_checked": len(output["photo_checks"]),
                          "photos_reachable": sum(check["ok"] for check in output["photo_checks"])}, indent=2))
        return
    recipes_file = pq.ParquetFile(RAW / "recipes.parquet")
    reviews_file = pq.ParquetFile(RAW / "reviews.parquet")
    recipe_ids = Counter()
    titles = Counter()
    categories = Counter()
    hosts = Counter()
    missing = Counter()
    flags = Counter()
    candidate_ids = set()
    ingredient_total = quantity_missing = 0
    samples = []
    eligible_seen = 0
    rng = random.Random(SEED)
    columns = ["RecipeId", "Name", "Description", "Images", "RecipeCategory", "Keywords",
               "RecipeIngredientParts", "RecipeIngredientQuantities", "RecipeInstructions",
               "TotalTime", "RecipeServings", "DatePublished"]
    for batch in recipes_file.iter_batches(batch_size=8192, columns=columns):
        for row in batch.to_pylist():
            recipe_id = canonical_id(row["RecipeId"])
            if recipe_id is None:
                flags["invalid_recipe_ids"] += 1
            else:
                recipe_ids[recipe_id] += 1
            for field in columns:
                value = row[field]
                if value is None or value == "" or value == []:
                    missing[field] += 1
            if has_text(row["Name"]):
                titles[row["Name"].strip().casefold()] += 1
            categories[row["RecipeCategory"] or "<missing>"] += 1
            images = [url for url in (row["Images"] or []) if has_text(url)]
            if images:
                flags["recipes_with_nonblank_image_links"] += 1
                for url in images:
                    hosts[urllib.parse.urlsplit(url).hostname or "<invalid>"] += 1
            parts = row["RecipeIngredientParts"] or []
            quantities = row["RecipeIngredientQuantities"] or []
            ingredient_total += len(parts)
            quantity_missing += sum(not has_text(item) for item in quantities)
            aligned = len(parts) == len(quantities)
            if not aligned:
                flags["ingredient_quantity_length_mismatch"] += 1
            if not usable_list(parts):
                flags["empty_or_blank_ingredient_lists"] += 1
            if not usable_list(row["RecipeInstructions"]):
                flags["empty_or_blank_instruction_lists"] += 1
            minutes = duration_minutes(row["TotalTime"])
            if minutes is None:
                flags["unparsed_total_time"] += 1
            elif minutes <= 0:
                flags["nonpositive_total_time"] += 1
            complete = recipe_id is not None and has_text(row["Name"]) and usable_list(parts) and usable_list(row["RecipeInstructions"])
            if complete:
                flags["required_fields_present_recipes"] += 1
            # Proposed display-review pool only. No model/training population filter.
            eligible = complete and aligned and images and minutes is not None and 0 < minutes <= 120
            if eligible:
                candidate_ids.add(recipe_id)
                eligible_seen += 1
                if len(samples) < 96:
                    samples.append(row)
                else:
                    slot = rng.randrange(eligible_seen)
                    if slot < len(samples):
                        samples[slot] = row
    print("Recipe checks complete", flush=True)

    ratings = Counter()
    pair_counts = Counter()
    review_ids = Counter()
    review_flags = Counter()
    users = set()
    users_rated = set()
    reviewed_recipes = set()
    date_min = date_max = None
    for batch in reviews_file.iter_batches(batch_size=32768, columns=["ReviewId", "RecipeId", "AuthorId", "Rating", "DateSubmitted"]):
        for row in batch.to_pylist():
            review_id = canonical_id(row["ReviewId"])
            if review_id is not None:
                review_ids[review_id] += 1
            else:
                review_flags["invalid_review_ids"] += 1
            recipe_id = canonical_id(row["RecipeId"])
            user_id = canonical_id(row["AuthorId"])
            if user_id is not None:
                users.add(user_id)
            else:
                review_flags["invalid_user_ids"] += 1
            if recipe_id is not None:
                reviewed_recipes.add(recipe_id)
            rating = row["Rating"]
            ratings[str(rating)] += 1
            joined = recipe_id in recipe_ids
            if not joined:
                review_flags["reviews_without_recipe_match"] += 1
            if rating not in (1, 2, 3, 4, 5):
                review_flags["not_explicit_1_to_5_rating"] += 1
            elif joined and user_id is not None:
                pair_counts[(user_id, recipe_id)] += 1
                users_rated.add(user_id)
                review_flags["explicit_rated_joined_rows"] += 1
                if recipe_id in candidate_ids:
                    review_flags["explicit_ratings_in_display_review_pool"] += 1
            date = row["DateSubmitted"]
            if date is None:
                review_flags["missing_dates"] += 1
            else:
                date_min = date if date_min is None else min(date_min, date)
                date_max = date if date_max is None else max(date_max, date)
    user_distinct = Counter(user for user, recipe in pair_counts)
    history_distribution = Counter(user_distinct.values())
    print("Rating/join checks complete", flush=True)

    # Category-diverse draft: two per category max from a seeded reservoir.
    selected = []
    selected_categories = Counter()
    for row in samples:
        category = row["RecipeCategory"] or "<missing>"
        if selected_categories[category] < 2 and len(selected) < 24:
            selected.append(row)
            selected_categories[category] += 1
    photo_checks = []
    if args.check_images:
        with ThreadPoolExecutor(max_workers=4) as executor:
            photo_checks = list(executor.map(probe_photo, selected[:args.check_images]))
    output = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(), "seed": SEED,
        "source_manifest": json.loads((RAW / "manifest.json").read_text(encoding="utf-8")),
        "pyarrow_version": pyarrow.__version__,
        "recipes": {"rows": recipes_file.metadata.num_rows, "columns": recipes_file.schema_arrow.names,
            "unique_ids": len(recipe_ids), "duplicate_id_rows": sum(count - 1 for count in recipe_ids.values()),
            "missing_fields": {field: missing[field] for field in columns}, "flags": dict(flags),
            "duplicate_normalized_title_rows": sum(count - 1 for count in titles.values()),
            "category_count": len(categories), "top_categories": categories.most_common(15),
            "image_url_hosts": hosts.most_common(), "ingredient_part_items": ingredient_total,
            "blank_quantity_items": quantity_missing, "display_review_pool_rows": eligible_seen},
        "reviews": {"rows": reviews_file.metadata.num_rows, "columns": reviews_file.schema_arrow.names,
            "unique_review_ids": len(review_ids), "duplicate_review_id_rows": sum(count - 1 for count in review_ids.values()),
            "unique_users_all": len(users), "unique_recipes_reviewed": len(reviewed_recipes),
            "rating_distribution": dict(sorted(ratings.items())), "flags": dict(review_flags),
            "date_min": date_min.isoformat() if date_min else None, "date_max": date_max.isoformat() if date_max else None,
            "users_with_joined_explicit_ratings": len(users_rated), "distinct_user_recipe_pairs": len(pair_counts),
            "repeat_explicit_user_recipe_rows": sum(count - 1 for count in pair_counts.values()),
            "user_history_histogram": dict(sorted(history_distribution.items())),
            "users_with_at_least_n_distinct_rated_recipes": {
                str(n): sum(count >= n for count in user_distinct.values()) for n in (2, 5, 10, 20)},
        },
        "photo_checks": photo_checks,
        "limitations": ["Photo HEAD checks test reachability/type, not visual correspondence or rights.",
            "Draft sample is category-diverse within a seeded photo/time/alignment-filtered reservoir, not a random dataset sample.",
            "Zero rating meaning is unconfirmed; never treat it as a dislike by default.",
            "No cleaned training split, model, metrics, frontend import, or validated cooking/allergy information."],
    }
    (OUT / "audit.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    if args.check_images:
        (OUT / "audit-with-photo-checks.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    # No reviewer names, review text or historical user IDs in the demo draft.
    (OUT / "catalog-review-draft.json").write_text(json.dumps(selected, indent=2, default=str) + "\n", encoding="utf-8")
    summary = {"recipes": output["recipes"]["rows"], "reviews": output["reviews"]["rows"],
               "recipe_flags": dict(flags), "review_flags": dict(review_flags),
               "rating_distribution": output["reviews"]["rating_distribution"],
               "history": output["reviews"]["users_with_at_least_n_distinct_rated_recipes"],
               "display_review_pool": eligible_seen,
               "photos_reachable": sum(check["ok"] for check in photo_checks), "photos_checked": len(photo_checks)}
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
