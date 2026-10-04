# ML 03: rating-trained collaborative factors and a bounded hybrid

Registered September 30, 2026 before model fitting or validation scoring. Approved scope: existing-rating collaborative training, new-user inference, and simple content/CF comparison. No app integration or final-test scoring.

## Question and fixed inputs

Do vectors learned from co-like patterns recover later recorded likes better than generic text vectors? Does combining the two help? This measures historical exact-recipe recovery, not every person's enjoyment of unreviewed food.

Preserve all ML 01 and ML 02 files. Reuse ML 01's fitting users, 5,006 ordered canonical candidates, 300 validation people, six earlier likes, seen exclusions, relevance (later 4–5 ratings), full-catalog ranking, and primary macro NDCG@10. Reuse the frozen original full-text MiniLM centroid as the content signal; do not select an ML 02 variant after seeing its results. Verify source artifact hashes. Reserved test rankings remain uncomputed. These are user-disjoint splits, not a globally chronological deployment simulation.

## One model, no training grid

- Weighted implicit ALS, implemented locally with NumPy/SciPy. Train 32-dimensional user and recipe factors, seed 20260930, 12 complete alternating user/item updates, regularization 1.0, positive extra confidence 20.0. Initialization: Gaussian recipe factors with standard deviation 0.01, float64. BLAS threads limited to one for reproducibility and small-solve efficiency; solve row blocks of 512.
- Use every fitting person with at least one candidate 4–5 rating; no history threshold chosen from validation. Binary deduplicated person/recipe positives. Source 1–3 ratings are not positive training pairs in this first model; retain them for diagnostics. Zero ratings were already excluded by ML 01. This is implicit *ranking preference*, not regression to exact star ratings.
- Minimize `sum_ui c_ui (p_ui - U_u dot V_i)^2 + lambda (||U||² + ||V||²)`. Recorded positives have p=1 and c=21; unobserved or nonpositive pairs have p=0 and c=1. The latter is a low-confidence optimization assumption, **not a verified dislike label**. No negative sampling. Record the exact objective after every full update and fail on non-finite values or a meaningful increase.
- Infer each new person's factor by the same regularized least-squares user update using only six unique seed likes and the fixed learned recipe factors. No later ratings, seen-only ratings, historical validation-user factors, or future labels enter inference. No cosine normalization of CF factors. Score by factor dot product, not probability. Empty profiles explicitly require a caller-chosen fallback; unknown recipe indices fail rather than silently fabricate a vector.
- Save factors and provenance locally under `data/processed/ml03`, outside frontend/public assets. Preserve all 5,006 items, including poorly connected ones. No diet-safety interpretation.

## Registered comparisons

Popularity; frozen full-text centroid; collaborative-only; three content/CF blends with CF weights 0.25, 0.50, 0.75. Scores are converted to within-person percentile ranks over unseen candidates (average rank for ties) before blending, avoiding incompatible raw score scales. Pure endpoints use raw component scores; monotone rank conversion preserves their ordering.

Also measure one deterministically shuffled CF-profile control, with the same ML 02 derangement and each recipient's own exclusions. This checks whether correct profile assignment adds signal beyond candidate popularity. It is not a full causal explanation.

Report all configurations. Any best validation blend is exploratory and selected on this validation set, not confirmed on final test. Include paired 2,000-person-bootstrap NDCG intervals versus popularity and CF; these are sample uncertainty, not a multiple-comparison correction or training-seed uncertainty. Do not force a blend to win or change hyperparameters after seeing results in this milestone.

## Diagnostics and verification

Report fitting rating counts, positive-history distribution, recipe coverage, co-like connectedness, iteration objectives, factor/artifact/code hashes, and runtime. Reproduce frozen baseline metrics. Use the same reconstructed validation histories for known-high/lower/unknown top-ten counts and observed-rating AUC (restricted subset, not whole-catalog quality). Inspect the existing six fixed case indices 0, 60, 120, 179, 239, 299; disclose later rating status and avoid claiming latent dimensions have human-readable meanings. These are not cherry-picked winners.

Tests: exact least-squares update versus a dense reference; training objective decreases; reproducibility; cross-recipe taste-group recovery in a synthetic fixture; duplicate, empty, unknown and non-finite input handling; blend endpoints/ties/exclusions; fitting/validation separation, artifact alignment, and frozen baseline reproduction. Re-run the local model deterministically and compare factor hashes. No network, extra packages, or UI changes needed.

## Interpretation

Collaborative filtering is itself an embedding method: representations are learned from ratings rather than semantic text similarity. It can capture cross-cuisine behavioral patterns, but also popularity, exposure and site-specific biases. New/unrated items and sparse users remain difficult. Content can complement cold start; a preference-trained text encoder or learned reranker is a later possibility, not included here.

Algorithm references: [Google matrix factorization](https://developers.google.com/machine-learning/recommendation/collaborative/matrix) and [collaborative filtering strengths/limitations](https://developers.google.com/machine-learning/recommendation/collaborative/summary).
