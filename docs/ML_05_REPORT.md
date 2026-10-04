# ML 05: final held-out evidence

Completed October 2, 2026 under the [registered protocol](ML_05_PROTOCOL.md). The selected raw co-like recommender beats fitting-only popularity on this independent, catalog-conditioned historical test. It remains strongly popularity-concentrated; niche discovery and nuanced taste prediction are not established.

## What was tested

The saved ML 04 raw model was frozen before final scoring. Each of 300 reserved historical people supplies six earlier positively rated recipes. Rank all unseen candidates from the same 5,006-recipe catalog; later 4–5-star ratings are the recorded relevant recipes. These are 300 of 936 eligible test people selected under the original deterministic procedure, not Expo visitors or the app user's personal profile. Fitting statistics use 305,920 unique positive user/recipe pairs from 86,845 people with fitting-catalog likes. Nothing was trained, downloaded, tuned or replaced in this milestone.

The six inputs simulate new-user preferences, but were not necessarily chosen from the app's six onboarding cards. The task is user-disjoint, not globally chronological: fitting ratings can occur after held-out seed dates. All 300 test profiles reconstructed exactly from the raw source histories. Original raw/popularity validation metrics reproduced exactly before final scoring.

## Final results

Higher is better for the first four rows. Precision/recall use recorded later likes, not assumed labels for unreviewed recipes.

| Measurement at ten recommendations | Popularity | Raw co-like |
| --- | ---: | ---: |
| People with at least one later recorded like | 84 / 300 (28.00%) | 107 / 300 (35.67%) |
| NDCG: recorded likes rewarded nearer the top | 0.05886 | 0.07202 |
| Precision: top-ten slots that recover recorded likes | 4.93% | 5.73% |
| Recall: average fraction of a person's recorded target likes recovered | 3.11% | 3.99% |
| Recovered-like slots across 3,000 recommendations | 148 | 172 |
| Distinct recommended recipes | 13 | 55 |
| Candidate-catalog coverage | 0.26% | 1.10% |
| Recommendation slots in fitting popularity's top 100 | 100.00% | 99.60% |
| Largest one-recipe share of all recommendation slots | 9.97% | 9.50% |

Raw-minus-popularity NDCG is **+0.01315**, with paired 2,000-bootstrap 95% interval **[+0.00705, +0.01924]**. Raw ranks recorded target likes better for 72 people, worse for 29 and identically for 199. The positive interval supports incremental value over popularity on this fixed task; it is not a universal accuracy or probability-of-enjoyment claim. Many ties include people for whom neither top ten recovered any recorded target.

The fixed shuffled-seed control has NDCG **0.06140** and hits for **91/300** people. Correct-minus-shuffled raw NDCG is **+0.01062**, interval **[+0.00381, +0.01765]**: 63 better, 43 worse, 194 tied. The actual person's seed assignments contribute useful signal in this control. A single derangement does not establish causal removal of popularity, exposure bias or complex latent taste understanding.

## Discovery and missing-label limits

Raw uses 55 distinct recipes across all test top tens, rather than popularity's 13, but **2,988 of 3,000 slots** are still in the fitting top 100. This is real personalization among mostly familiar, common recipes, not a demonstrated long-tail discovery system. The 5,006 addressable candidates remain intact; source coverage does not mean they are equally likely to be recommended.

Raw's top tens contain **172 known later high ratings, 5 known later lower ratings, and 2,823 unknown ratings**. Unknown is 94.1% of slots; it is not a dislike. Popularity has 148 high, 8 lower and 2,844 unknown. The narrow observed-rating AUC diagnostic uses only 95 people with both high and lower future ratings: raw **0.51316**, popularity **0.51533**. Thus broad high-versus-lower taste discrimination is not established even though top-ten recovery improves. AUC answers a different, selected-subset question from NDCG and cannot turn unknown recipes into negatives.

Reconstructed test histories contain 22,550 later positive records across all canonical content; 5,956 lie in the fixed candidate catalog (**26.41% pooled coverage**). Mean per-person positive coverage is **49.83%**; it differs because very long histories weigh more in the pooled count. The benchmark only judges in-catalog positives. Of these in-catalog targets, **13.16%** are in the fitting top 100. Candidate/active-reviewer selection, incomplete self-selected ratings and remaining near duplicates limit generalization. None proves that simply adding more data solves the concentration issue.

## Does the running product use the same top tens?

The existing Discover engine was called in-process for all 300 people, giving it their likes and excluding the other earlier-seen recipes. Its top-ten lists agree with the frozen raw benchmark for **300/300** profiles; its aggregate metrics are identical and none of these top-ten slots needs zero-connection popularity fallback. The fallback still exists farther down lists and for no-evidence profiles. No product rule was modified. This checks the existing serving code, not a live browser session, arbitrary profile sizes, ingredient search or group satisfaction.

## Verification and reproducibility

- 96 Python tests pass, including 13 new final-evaluation fixtures and existing artifact, HTTP, ingredient and group checks. An initial sandbox run failed three temporary-file fixtures on Windows access permissions; the full suite passed outside the sandbox before registration and was rerun after scoring.
- Synthetic fixtures cover metric arithmetic, fixed shuffle, label-independent scores, primary/serving ordering, exclusions, profile validation, immutable registration and write-once run guards.
- Registered code/document/input hashes match; every top-level ML 01–04 artifact is unchanged. The new final receipt verifies without rescoring.
- Independent arithmetic/exclusion checks of the stored 1,200 top-ten lists (popularity, raw, shuffled and serving) reproduce their NDCG and hit counts without computing model scores again.
- No frontend/backend serving code, model weights, recipe metadata or personal/guest storage was changed. No new frontend build, browser review or quality claim for Ingredients/MealMerge is included.

Use the existing `.venv` and local ignored artifacts:

```powershell
# The run is complete. Audit without recomputing test rankings:
.\.venv\Scripts\python.exe scripts/run_final_evaluation.py verify
.\.venv\Scripts\python.exe -m unittest discover -s scripts -p 'test_*.py' -v
```

The original workflow was `prepare`, then `evaluate`. Both refuse overwrites; `evaluate` now refuses a second run because the exclusive start marker exists. Do not delete it or retune against these outcomes. An interrupted future copy requires explicit audit, not a silent retry. The existing older artifact tests can integrity-check reserved profile structure without scoring it. Frozen predecessor `test_scored: false` fields correctly describe their historical runs; the unchanged service's static `testScored: false` health field is **not** current project-wide evaluation status. ML 05 `results.json` explicitly records `test_scored: true`.

Local files: `data/processed/ml05/{protocol.json,test-started.json,histories.json,rankings.json,results.json,completion.json}`. Historical keys and detailed rankings remain local/ignored, not Expo-facing. Packages: NumPy 2.5.3, SciPy 1.18.1, PyArrow 25.0.1. Full code/predecessor hashes are in the local receipt.

| Receipt | SHA-256 |
| --- | --- |
| Registration JSON | `b843bdedee436bdbde9c73902c46833ad3762495d416e4b55f3528b7bde883b4` |
| Aggregate results JSON | `135420284cfb4135acd9301f9b01d68b552142552d58c5e58e218a39f7e10a17` |
| Stored rankings JSON | `04cd1c61974b9e7d69aa6295bf8ee03f05956176f90d7eab521b309ec7f7b85a` |
| Reconstructed histories JSON | `e3ef11f47ff5eb0c1d2360c7aaa35c7528c4367e4a4bcfe2821b0e54073c70a8` |

## Outcome and next discussion

Keep the current selected model unchanged: this test supports it over popularity for the frozen individual-ranking task, not every product ambition. Do not add a learned hybrid/XGBoost layer or assert nuanced/niche preferences because the test passed. See [plain-language Expo evidence](EXPO_ML_EVIDENCE.md). Propose an end-to-end demo/rehearsal and bounded reliability review next; implementation needs a separate agreement. MealMerge trade-off review remains deferred at the user's request.
