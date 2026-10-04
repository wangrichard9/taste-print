# ML 02: bounded content diagnosis

Approved after the user asked to investigate the root of ML 01's weak content result. This is a predeclared validation experiment, not deployment or a new claim of original model training. ML 01 source artifacts, results, and reserved final test remain unchanged.

## Fixed controls

Reuse the exact 300 ML 01 validation profiles, six likes, seen exclusions, 5,006 source-ID-aligned candidates, 4–5-star relevance rule, source version/hashes, and pretrained MiniLM revision. Do not add evaluation people, recipes, sampled negatives, or new model weights. No app changes, original neural training, collaborative filtering, or XGBoost. Use installed packages and the already downloaded local model.

## Registered six comparisons

Cross two recipe-text representations with three profile scoring rules:

- Full: the existing ML 01 source name, ingredient names, category, and keywords; reuse frozen embeddings.
- Ingredients: `Ingredients: <source ingredient names>.` No added aliases, inferred ingredients, quantity filtering, stopword removal, or field weighting. Encode with the same model/settings.
- Centroid: cosine similarity to the normalized mean of six normalized liked vectors (original rule).
- Closest: maximum cosine similarity to any of the six liked recipes.
- Top two: mean of the two greatest individual seed similarities for each candidate.

This isolates text changes at fixed profile rules and profile changes at fixed text. Ingredient-only changes several fields together, so any improvement cannot establish which removed field was responsible. Averaging all six individual cosine scores is proportional to centroid scoring and is not an independent ranking method; test this equivalence.

Primary metric: macro binary NDCG@10, alongside Precision@10, Recall@10, HitRate@10, catalog coverage and recommendation concentration. Recompute popularity and original centroid scores to verify exact reproduction against the frozen ML 01 aggregate. Report paired seeded bootstrap intervals for changes from full/centroid (2,000 resamples), explicitly exploratory without correction for multiple comparisons. No claiming a tuned winner is a final-test result.

## Diagnostic probes, not substitute benchmarks

1. Re-encode eight deterministically sampled full-text recipes and compare with corresponding frozen vector rows. Verify finite normalized vectors and source text alignment. This can find an indexing/encoding error, not prove general model quality.
2. Score original full/centroid with other people's six-like profiles through a seeded derangement. Keep each recipient's actual seen exclusions and withheld labels. Compare with correct profiles: a single shuffled control tests personalization signal in this sample, not absence of all possible preference signal.
3. Reconstruct only the 300 validation people's valid canonical source histories. Verify each stored profile's seeds, cutoff, exclusions and target IDs against raw ratings. Measure later positive records outside the catalog, and target popularity concentration. More candidate recipes would expand coverage but also make ranking harder; low coverage alone cannot explain the gap between two methods with identical candidates.
4. On people with both later 4–5-star and later 1–3-star candidate ratings, compute paired score discrimination (AUC, including half credit for ties). These are **observed higher versus lower ratings**, not fabricated negatives. This restricted, selection-biased diagnostic is not the full-candidate top-ten benchmark and must never replace it.
5. For every method, report how many of the 3,000 recommendations have a known later high rating, known later lower rating, or no later rating from that person. Unrated recommendations are unknown, not proven dislikes.
6. Inspect a fixed set of six validation cases (evenly spaced profile indices 0, 60, 120, 179, 239, 299), regardless of outcome. Include seeds, top results, exact rating-status labels, closest seed/shared ingredients, and withheld positives. Do not infer actual enjoyment from apparent resemblance. Local detailed cases stay in ignored processed data; published notes omit user keys.

No diagnosis of a specific root cause before results. Predicted signals: if averaging is the main weakness, closest/top-two scoring should improve at fixed text; if mixed text is the main weakness, ingredient-only should improve at fixed scoring; if label coverage is a major limitation, many top results should be unrated and reviewed-item discrimination may differ from exact full-catalog recovery. These probes can constrain explanations, not prove that missing labels are the sole cause.

## Artifacts and stopping rule

Use a separate ignored `data/processed/ml02` directory. Freeze its protocol and ingredient vectors; retain hashes of all ML 01 inputs before/after. Record the complete registered grid and diagnostics, including negative results, not an open-ended search until a method wins. Final test remains unscored. Save aggregate evidence and a plain-language report in docs, then discuss further changes with the user.
