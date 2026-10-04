"""Download the approved local audit inputs; never read or request credentials."""
import argparse
import hashlib
import json
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "irkaal/foodcom-recipes-and-reviews"
VERSION = 2
BASE = "https://www.kaggle.com/api/v1/datasets"
FILES = ("recipes.parquet", "reviews.parquet")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    destination = ROOT / "data/raw/foodcom-v2"
    destination.mkdir(parents=True, exist_ok=True)
    listing_url = f"{BASE}/list/{SOURCE}"
    with urllib.request.urlopen(listing_url, timeout=45) as response:
        listing = json.load(response)
    sizes = {item["name"]: item["totalBytes"] for item in listing["datasetFiles"]}
    manifest = {
        "source": f"https://www.kaggle.com/datasets/{SOURCE}",
        "version": VERSION,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "intended_use": "local temporary Tasteprint Expo demo and data audit",
        "stated_license": "CC0: Public Domain (uploader label, not an independent rights determination)",
        "file_listing_url": listing_url,
        "files": [],
    }
    for name in FILES:
        url = f"{BASE}/download/{SOURCE}?" + urllib.parse.urlencode({
            "dataset_version_number": VERSION, "file_name": name,
        })
        target = destination / name
        if not target.exists():
            partial = destination / f"{name}.download"
            print(f"Downloading {name} (version {VERSION})", flush=True)
            with urllib.request.urlopen(url, timeout=60) as response:
                content_type = response.headers.get("Content-Type", "")
                if "html" in content_type or "json" in content_type:
                    raise ValueError(f"Unexpected response type: {content_type}")
                with partial.open("wb") as stream:
                    downloaded = 0
                    milestone = 0
                    while block := response.read(1024 * 1024):
                        stream.write(block)
                        downloaded += len(block)
                        if downloaded // (25 * 1024 * 1024) > milestone:
                            milestone = downloaded // (25 * 1024 * 1024)
                            print(f"  {downloaded / 1024**2:.0f} MiB", flush=True)
            if zipfile.is_zipfile(partial):
                with zipfile.ZipFile(partial) as archive:
                    matches = [info for info in archive.infolist() if info.filename == name]
                    if len(matches) != 1:
                        raise ValueError("Archive does not contain the expected exact file")
                    # Copy one verified member, never extract arbitrary archive paths.
                    with archive.open(matches[0]) as source, target.open("xb") as output:
                        for block in iter(lambda: source.read(1024 * 1024), b""):
                            output.write(block)
                partial.unlink()
            else:
                partial.rename(target)
        with target.open("rb") as stream:
            if stream.read(4) != b"PAR1":
                raise ValueError(f"{name} is not Parquet")
        if target.stat().st_size != sizes[name]:
            raise ValueError(f"{name} size differs from current listing; check dataset version")
        manifest["files"].append({"name": name, "bytes": target.stat().st_size,
                                   "sha256": sha256(target), "download_url": url})
        print(f"Verified {name}: {target.stat().st_size:,} bytes", flush=True)
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("Local source manifest saved.", flush=True)


if __name__ == "__main__":
    main()
