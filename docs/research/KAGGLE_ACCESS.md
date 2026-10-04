# Kaggle access for the local Tasteprint audit

Checked September 30, 2026. This is an access note, not model training or a public-distribution decision.

## Supported access

Kaggle's first-party announcement permits unauthenticated public dataset downloads through its API; website downloads still require login. Current KaggleHub documentation says authentication is needed for private resources or public resources requiring consent. Its integration tests explicitly cover unauthenticated public dataset downloads. [Kaggle announcement](https://www.kaggle.com/product-announcements/485439), [KaggleHub documentation](https://github.com/Kaggle/kagglehub#authenticate), [integration tests](https://github.com/Kaggle/kagglehub/blob/main/integration_tests/test_dataset_download.py).

The documented Python interface supports a versioned handle plus a single-file path, for example `kagglehub.dataset_download('irkaal/foodcom-recipes-and-reviews/versions/2', path='recipes.parquet', output_dir='./data/raw/foodcom-v2')`. No package installation or download was performed for this reference check. [Download documentation](https://github.com/Kaggle/kagglehub#download-dataset).

## Direct HTTP route verified in official source

KaggleHub v0.3.13's official resolver constructs these API paths; its client uses the `api/v1` prefix. The current implementation uses the SDK but retains equivalent owner, dataset, version, and file request fields. [Version-pinned resolver source](https://github.com/Kaggle/kagglehub/blob/v0.3.13/src/kagglehub/http_resolver.py), [HTTP client source](https://github.com/Kaggle/kagglehub/blob/v0.3.13/src/kagglehub/clients.py), [current resolver source](https://github.com/Kaggle/kagglehub/blob/main/src/kagglehub/http_resolver.py).

- Metadata: `https://www.kaggle.com/api/v1/datasets/view/irkaal/foodcom-recipes-and-reviews`; read `currentVersionNumber` before pinning.
- Version 2 recipe file: `https://www.kaggle.com/api/v1/datasets/download/irkaal/foodcom-recipes-and-reviews?dataset_version_number=2&file_name=recipes.parquet`.
- Version 2 review file: `https://www.kaggle.com/api/v1/datasets/download/irkaal/foodcom-recipes-and-reviews?dataset_version_number=2&file_name=reviews.parquet`.
- CSV alternatives: same pinned route with `file_name=recipes.csv` or `file_name=reviews.csv`.

Follow standard redirects; do not reuse or publish time-limited signed storage URLs. Check the downloaded response type before parsing: Kaggle can wrap a single large file in ZIP. The official client handles that case explicitly. [Download handling](https://github.com/Kaggle/kagglehub/blob/v0.3.13/src/kagglehub/clients.py).

## Practical file choice

The uploader recommends Parquet because it preserves the schema. Recipe CSV list columns use R-style strings, so Parquet avoids a separate safe list parser. Never evaluate CSV list strings as code. [Dataset card](https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews).

The main audit agent separately verified unauthenticated metadata/list responses for this release: version 2, dataset ID 1063627, license label CC0, `recipes.parquet` 178,723,234 bytes and `reviews.parquet` 173,762,142 bytes (352,485,376 bytes together before any transport compression). CSV alternatives are 704,213,964 and 496,098,450 bytes. These are API-reported sizes, not a completed local download measurement. [Dataset API search](https://www.kaggle.com/api/v1/datasets/list?search=foodcom-recipes-and-reviews), [file list API](https://www.kaggle.com/api/v1/datasets/list/irkaal/foodcom-recipes-and-reviews).

Record version, original dataset link, file hashes, actual sizes, and retrieval date in the local audit manifest. Keep raw files outside the frontend bundle and ignored by version control. This preserves reproducibility without publishing the dataset.
