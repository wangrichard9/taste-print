# ML 01: six choices to content recommendations

Approved September 30, 2026 after the user confirmed the hybrid direction and asked for the next step. This first slice evaluates content recommendations; it does not replace the planned collaborative/hybrid work.

## What Tasteprint does here

Six explicit liked recipes become a food-preference vector. Candidate recipes are ordered by similarity to that vector, excluding recipes already seen. This runs in Python, not Discover yet. No accounts, backend, cloud inference, LLM ingredient extraction, collaborative model, XGBoost, or MealMerge is included.

Reused: [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), a generic short-text encoder, pinned to revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`. Its output has 384 dimensions; the model's default input limit is 256 word pieces. This is not a food-specific preference model. Tasteprint does not fine-tune its weights in this milestone. See [the provider's usage documentation](https://www.sbert.net/docs/sentence_transformer/usage/usage.html).

Implemented by Tasteprint: source-text assembly, duplicate handling, held-out user protocol, six-like profile construction, seen-item exclusion, deterministic ranking, training-user-only popularity statistics, and evaluation. The mean-of-likes rule is hand-authored, not a learned ranker. Similarity is a ranking score, never a probability or allergy assessment.

## Frozen protocol

Inputs are the audited `irkaal/foodcom-recipes-and-reviews` version 2 Parquet files. Preparation verifies both download-manifest file hashes. Only valid IDs, nonblank recipe names/ingredient lists, explicit ratings 1–5, and dated reviews enter the experiment. Zero is not a dislike. Names/ingredients/category/source keywords enter the encoder; descriptions, cooking steps, rating counts, authors, review text, and editorial display summaries do not.

Recipes with identical normalized names and sorted ingredient names share the lowest source ID as their canonical identity. Per-user repeats of that identity collapse to the earliest dated explicit rating; future repeats are not averaged into the past. This removes conservative exact duplicates, not all near duplicates.

User partitions are deterministic and disjoint: SHA-256 of `20260930:<source user ID>`, modulo 100; 0–79 fitting, 80–89 validation, 90–99 reserved test. No evaluation user's ratings contribute to popularity. Generated local artifacts contain pseudonymous user keys, not names/review text. Raw data retains its existing local-only scope.

The candidate catalog is the 5,000 most positively rated canonical recipes **among fitting users**, with source-ID tie breaking, plus the 30 already approved demo recipes mapped to canonical identities. This intentionally bounds laptop computation and keeps app inputs addressable. Images and quantity alignment are not model-population filters. Selection uses fitting users only, never validation/test target labels or the source's full-data aggregated rating/count columns.

Each evaluation user's history is restricted to that fixed catalog. Their first six 4–5-star recipes in chronological order form the profile. All recipes observed at or before the sixth-like timestamp are excluded from recommendations, including earlier 1–3-star recipes. Later-time 4–5-star recipes are the withheld positives; equal-time events are not future evidence. People without six seeds plus a later positive are excluded. Up to 300 eligible people per held-out partition are selected in deterministic hash order, not by model performance.

This is **catalog-conditioned new-user evaluation**, not a worldwide/full-catalog benchmark or global future forecasting. Fitting users may have ratings later than evaluation seed dates. Candidate coverage and eligible/evaluated user counts must accompany results.

## Two methods on the same task

- Popularity: descending number of fitting-user 4–5-star ratings; unchanged across profiles except seen exclusions.
- Semantic content: encode each source recipe, normalize its vector, average the six unique liked vectors, normalize that mean, then rank by cosine similarity. Source-ID tie breaking is deterministic.

Both rank every eligible candidate, rather than comparing a target against a small, easy random-negative sample. No pass penalty, recipe generation, or dietary constraints are inferred. Later low ratings do not become onboarding input.

Validation is measured in ML 01. Test labels are prepared and integrity-checked, but **test rankings/metrics remain uncomputed** until an agreed final evaluation. Do not repeatedly tune against test data. Changing preprocessing/candidates/splits requires a new experiment directory/protocol; the preparation command refuses to overwrite an existing protocol.

## Reading the measurements

At K=10, per-person results are averaged equally:

- Precision: how many of the top ten are recorded withheld likes, divided by ten.
- Recall: what fraction of that person's recorded withheld likes appear in the top ten.
- NDCG: rewards putting recorded withheld likes closer to the top, relative to an ideal ranking.
- Hit rate: fraction of people with at least one withheld like in the top ten.
- Catalog coverage: fraction of candidate recipes recommended to anyone in the measured group.

A paired seeded bootstrap interval over the validation users describes variability in the semantic-minus-popularity NDCG difference. It does not establish performance for Expo visitors or calibrate a liking probability.

## Limits and the hybrid destination

Ratings are positive-heavy and self-selected. Unreviewed recipes may still be liked; misses are not proven dislikes. Popularity-based candidate selection favors head recipes, and qualifying active reviewers are not representative of every new person. The chosen six likes simulate onboarding, rather than matching the app's current six displayed choices exactly. Metadata may be incomplete; text truncation is measured, and near-duplicate content may still inflate results. Results must be interpreted with these restrictions.

Next scopes remain discussions: train collaborative filtering on fitting-user histories; design how an Expo visitor's likes connect to collaborative item representations; compare a simple hybrid and, if justified, a trained XGBoost ranking layer. App integration, larger onboarding, custom dishes, and MealMerge remain separate approvals.

## Reproduce locally (PowerShell)

Use the existing project `.venv` with Python 3.12 and the audited source files. For a fresh environment, install the CPU build first, then the frozen environment dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install torch==2.14.1+cpu --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements-ml.txt
.\.venv\Scripts\python.exe scripts/prepare_recommendation_data.py
.\.venv\Scripts\python.exe scripts/run_recommendation_experiment.py encode --download-model
.\.venv\Scripts\python.exe scripts/run_recommendation_experiment.py evaluate
.\.venv\Scripts\python.exe -m unittest discover -s scripts -p 'test_*.py' -v
```

Preparation refuses to replace a frozen protocol. If this project's artifacts already exist, skip preparation and encoding; `evaluate` reuses verified vectors without network or model loading. Calling `encode` again verifies the existing cache and does not overwrite it. Without `--download-model`, encoding allows local model files only. The first download uses public weights, no account/API key or remote inference, and stores the model under ignored `data/processed/ml01/model-cache`.

Try a custom profile using real source IDs from the app catalog:

```powershell
.\.venv\Scripts\python.exe scripts/run_recommendation_experiment.py recommend --likes foodcom:90975,foodcom:28199 --demo-only
```

The example likes the catalog's Greek salad and baked salmon. Replace those IDs with others actually present in `src/data/recipes.json`; unknown IDs fail rather than being guessed. `--demo-only` limits results to the approved display catalog. Without it, outputs can include recipes never manually reviewed for display, so do not automatically publish those results into Discover. The recommender accepts one or more likes; evaluation specifically uses six. The scripts do not alter browser choices or the frontend catalog.

Outputs: frozen `protocol.json`, source-text `catalog.json`, fitting-only `train.parquet`, held-out `validation.json` and reserved `test.json`, a demo identity map, normalized `embeddings.npy`, encoder provenance `embeddings.json`, and `validation-results.json`, all under ignored `data/processed/ml01`. Keep aggregate report evidence in documentation; do not bundle historical profiles or the bulk artifacts into the app.
