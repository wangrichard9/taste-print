# Local recipe-data audit 01

Completed September 30, 2026 (America/Los_Angeles). Approved scope: a practical access-and-quality audit for a local temporary Expo demo, not publication, app integration, or model training.

## Outcome in Tasteprint terms

We now have actual recipe metadata and individual ratings on disk, rather than only source-reported numbers. This is a workable candidate for a real Discover catalog and subsequent recommendation experiments. The app itself still shows the six illustrative dishes; its preference summary is not a trained model.

Source: [Food.com Recipes and Reviews, uploader irkaal](https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews), version 2. Public downloads succeeded without credentials. Source attribution and the uploader's stated CC0 label are retained in `THIRD_PARTY_NOTICES.md` and the local manifest. No exhaustive rights review was performed; local use and attribution are not asserted to establish every contributor/photo permission. Revisit requirements if the user decides to publish.

## Measured results

These are full-file local measurements, except the explicitly limited photo sample.

| Check | Result |
| --- | --- |
| Recipes | 522,517; 522,517 unique IDs |
| Reviews | 1,401,982; no duplicate review IDs |
| Distinct historical reviewers | 271,907 |
| Reviews without a matching recipe | 19 |
| Recipes with at least one nonblank photo URL | 165,896 (31.7%) |
| Recipes with name, nonblank ingredients, and nonblank steps | 520,265; field presence, not proof of correctness |
| Ingredient/quantity list-length mismatches | 407,536 (78.0%) |
| Structurally filtered display-review pool | 34,559 recipes |
| Limited photo-header checks | 24/24 returned HTTP 200 with an image content type |
| Users with at least 10 distinct joined, explicitly rated recipes | 14,543 |

### What needs care

**Ingredient lists are not automatically full shopping lists.** Never pair different-length ingredient/quantity arrays by position or silently truncate them. Even aligned lists may lack quantity text, units, or ingredients mentioned in instructions. The audit checks structure, not cooking accuracy. A later small demo catalog needs manual content/photo review; do not infer dietary safety from these fields.

The display-review pool requires a valid ID, name, nonblank ingredients/steps, aligned ingredient/quantity array lengths, a photo URL, and a parseable total time greater than zero and at most 120 minutes. This is a proposed display filter, not an approved training population. A seeded reservoir of 96 records supplied a 24-record category-diverse draft, with no more than two per category. It includes unsuitable editorial choices such as seasoning mixes and cocktails: it is **not the final demo catalog**.

All 408,990 nonblank image links point to `img.sndimg.com`. The 24 HEAD requests checked only the first URL for selected draft records. No images were downloaded, and visual correspondence, offline availability, and database-wide link reliability were not verified. This filtered sample is not a random estimate of total photo usability.

**Ratings are strongly positive-heavy.** There are 1,325,716 joined 1–5-star ratings, covering 234,634 users, with no repeated user/recipe pair among those rows. Overall rating counts are: zero 76,248; one 16,559; two 17,597; three 50,279; four 229,217; five 1,012,082. About 76.3% of explicit ratings are five stars. Zero's meaning remains unconfirmed: do not automatically treat it as a dislike. These counts describe the collection, not model performance.

There are 26,400 users with at least five distinct joined explicit ratings, 14,543 with at least ten, and 7,938 with at least twenty. That supports investigating held-out preference evaluation, but a split, relevance definition, baselines, and negative-signal policy still need agreement. Reviewed dates span January 2000–December 2020; this is historical taste data, not current Food.com activity.

Normalized titles have 85,606 duplicate rows beyond the first occurrence. Different recipes can share titles; preserve source IDs and never merge by name. Potential recipe-content leakage across future evaluation splits has not been resolved.

## Implementation and reproduction

- `scripts/download_foodcom.py`: version-pinned public download, format/size checks, optional ZIP-wrapper handling, SHA-256 manifest. Does not read credentials.
- `scripts/audit_foodcom.py`: batched recipe/review checks, explicit ID validation, join/history counts, seeded display-review draft, optional allowlisted photo HEAD requests. No reviewer names or review text are exported into the draft.
- `requirements-data.txt`: isolated reader environment, PyArrow 25.0.1 and tzdata 2026.4. Tested on Python 3.12.14 on Windows; timezone data is needed by the reader there.
- `.gitignore`: raw/processed data and the environment stay out of version control. Nothing was copied into `public/` or the frontend bundle.

From the project root, with Python 3.12 available:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-data.txt
.\.venv\Scripts\python.exe scripts/download_foodcom.py
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s scripts -p test_data_audit.py
.\.venv\Scripts\python.exe -X utf8 scripts/audit_foodcom.py --check-images 24
```

Omit `--check-images 24` for an entirely offline audit of already-downloaded files. That run replaces `audit.json` with results without network probes; it does not assert previous links still work. A network-checked snapshot is retained separately as `audit-with-photo-checks.json`. Use `--photos-only --check-images 24` to refresh photo-header checks for the existing draft without repeating full-file processing.

Local outputs:

- `data/raw/foodcom-v2/recipes.parquet`: 178,723,234 bytes, SHA-256 `9f591abe9f8d1c691bbc630b0431ec6613f09fabe93f1789af87a06484aae9fb`.
- `data/raw/foodcom-v2/reviews.parquet`: 173,762,142 bytes, SHA-256 `439da8db7c7af03a368c41957cb56fb6e4f43f0786aa744ecd816a6f959748f0`.
- `data/raw/foodcom-v2/manifest.json`: provenance and actual retrieval time.
- `data/processed/foodcom-v2/audit.json`: reproducible full-file aggregate results.
- `data/processed/foodcom-v2/audit-with-photo-checks.json`: separately retained 24-probe results with their audit provenance.
- `data/processed/foodcom-v2/catalog-review-draft.json`: draft records for discussion, not frontend content.

Verification: both files downloaded and matched API-reported sizes; all rows were processed; four helper tests pass (IDs, list text, durations, and photo host restrictions). The measured offline rerun is recorded separately from the photo-header check. No UI code changed. No cleaned training dataset, backend, trained model, evaluation scores, or personalized recipe ranking was produced.

## Proposed next discussion

Recommend a small, manually reviewed real-recipe Discover catalog before ML integration. Preserve IDs/source attribution, use existing visual standards, exclude misleading ingredient/quantity pairings, and retain honest missing-image behavior. The 24-record draft is not a finished selection. Discuss demo internet availability before deciding whether to download local photo assets.

After catalog scope is agreed, discuss an explainable content baseline and a held-out evaluation protocol separately. Do not present fixed catalog order, average stars, or tag counts as a learned recommender.
