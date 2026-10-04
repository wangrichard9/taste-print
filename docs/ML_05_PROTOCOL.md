# ML 05: independent final evaluation

Approved October 2, 2026. Registered before final-test ranking or result inspection. Reserved profiles were already prepared and integrity-checked under ML 01; existing integrity tests can read their structure without scoring them. This closes the selected individual-recommendation experiment; it is not another method search.

## Frozen question and methods

Does the previously selected raw co-like recommender recover later recorded likes better than fitting-only popularity for new historical people given six earlier likes?

Primary comparison: saved ML 04 `direct/raw` versus original popularity. Reuse the fixed 5,006 candidates, source-ID tie breaking, all earlier-seen exclusions, binary later 4–5-star relevance and 300 reserved test people from ML 01. Score all eligible candidates, not sampled negatives. No refitting, parameter changes, semantic/ALS comparison grid, learned hybrid, new data or dependencies. Do not promote a replacement or tune after seeing these results.

Secondary personalization diagnostic: one fixed derangement of the test seed profiles using seed 20260930, retaining each recipient's original exclusions and targets. Compare correct minus shuffled raw NDCG; donor seeds are not extra recipient exclusions. This is a control, not a product method or a causal proof.

Serving-alignment diagnostic: call the existing Discover engine in-process with each person's six likes and other earlier-seen recipes as exclusions. It ranks positive raw connections first, with source-ID ties, then uses fitting popularity for zero-connection fallback. Report its top-ten metrics, fallback slots and number of lists differing from the frozen benchmark. This does not change the app. Serving and historical metrics are kept distinct even if their top tens agree. No ingredient or group-quality evaluation is included.

## Measurements fixed in advance

Primary: macro binary NDCG@10, which rewards later recorded likes near the top. Secondary: precision, recall and hit rate at ten, recovered-like count, unique recommended recipes/catalog coverage, fitting top-100 recommendation share and largest single-recipe share. Compare raw minus popularity with a paired 2,000-person-bootstrap 95% percentile interval (seed 20260930); also report better/worse/tied people and the registered correct-minus-shuffled contrast. These intervals describe sampled-person variability, not a liking probability or training-seed variability. No minimum effect or significance claim is inferred from a positive point estimate alone.

Reconstruct the 300 raw histories using the existing canonicalization and verify exact agreement with their frozen profiles. Report known later high/lower/unknown recommendation slots, restricted observed-rating AUC for raw/popularity, pooled and mean-person future-positive candidate coverage, and held-out positive concentration in the fitting top 100. Unknown ratings remain unknown, not dislikes. Report evaluated versus eligible people (300 of the previously registered 936 eligible test people).

## Registration, one-way test use and verification

`run_final_evaluation.py prepare` verifies the old protocols, hashes all top-level ML 01–04 artifacts, this document, the scoring/evaluation/serving implementations and its fixture tests, without deserializing `test.json`. It refuses to overwrite registration. Run synthetic-fixture tests before preparation. The code and inputs are checked again before scoring.

`evaluate` first reproduces the selected raw/popularity validation metrics exactly from saved histories. Before opening test profiles it creates an exclusive `test-started.json` marker. A second run refuses to score again, including after interruption; investigate an interrupted run explicitly rather than silently unsealing a fresh test. New outputs go only into ignored `data/processed/ml05`; previous artifacts and browser preferences remain untouched. Detailed historical keys/rankings stay local, not in Expo-facing evidence.

Record completed aggregate results, local ranking/history hashes, registration hash, package versions and unchanged predecessor hashes. A separate completion receipt hashes the aggregate result file. `verify` checks the completed receipt without rescoring. Historical ML 01–04 `test_scored: false` fields describe those original runs and must remain immutable; the new ML 05 receipt is authoritative for final-test completion. The unchanged service's static health flag is not a project-wide evaluation status.

Test fixtures cover primary/serving fallback ordering, unseen exclusions, exact metric arithmetic, unknown labels, profile validation, fixed derangement, paired intervals, future-label-independent scoring, write-once outputs and registration without opening test profiles. Run the full Python suite and receipt verification. No frontend changes, UI review or browser demo is claimed by this Python/docs milestone.

## Interpretation and stopping

All outcomes are reported, including a loss or an inconclusive interval. The test is user-disjoint, not globally chronological; candidates and eligible people are conditioned on an active-reviewer/head-heavy catalog. Missing ratings, self-selection, near duplicates and selection on reused validation constrain interpretation. Six historical earlier likes do not exactly simulate Expo onboarding and do not establish quality for arbitrary profile sizes. No proof of nuanced taste, niche discovery, allergy safety, sensory annotation accuracy or MealMerge satisfaction follows from individual ranking metrics.

Stop after the frozen evaluation and plain-language evidence report. Discuss demo rehearsal/remaining polish with the user separately; MealMerge trade-off review is explicitly deferred.
