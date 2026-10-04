# ML 04: a direct collaborative foundation is the provisional choice

September 30, 2026. Approved comparison complete: two direct co-like methods and three fixed ALS confidence/regularization variants. This report recommends an approach to discuss and validate next, not an already integrated or independently confirmed final hybrid. App behavior, all previous experiments, and final-test rankings are unchanged.

## Outcome in Tasteprint terms

**Direct item-to-item collaborative ranking is now the strongest measured behavioral foundation.** Rather than compress people/recipes into latent vectors, it learns a table of which recipes historical fitting people liked together. A new person's six likes select those relationships; the resulting scores rank unseen dishes. Raw shared-like counts have the highest registered behavioral validation NDCG@10, slightly ahead of popularity. Correct profile assignment contributes measurable signal in this fixed shuffle comparison. The normalized/shrunk method is a useful alternative with broader recommendation coverage, but lower primary ranking performance.

This is still collaborative filtering, not semantic matching. The relationship table is fitted from ratings. It is an empirical model, not neural training, latent taste embeddings, or an XGBoost combining model. The codebase-design skill shaped an independently testable module for fitting and scoring without changing the old CF module or frontend. We did train three additional latent-factor models, but none overtakes the direct methods. We should not choose a more complicated model just for a stronger training story.

## Fixed experiment

Same Food.com version-2 fitting data and ML 01 task: 305,920 binary 4–5-star pairs from 86,845 fitting people, 5,006 canonical candidates, and 300 user-disjoint validation profiles with six earlier likes. Rank all unseen candidates; recover later recorded 4–5 positives. No raw-data download, extra package, encoder change, XGBoost, backend or app integration. Labels/candidate limitations from ML 02 persist. The dataset is user-disjoint, not globally chronological.

Choices were registered in `ML_04_PROTOCOL.md` before fitting/scoring. Direct/raw averages shared-fitting-liker counts across unique seed recipes. Direct/cosine_shrunk normalizes each shared count by both recipe positive counts and multiplies by `support/(support+10)` to discount weak links. Self-links are zero. Three new ALS fits vary confidence increment 5/20 and regularization 1/10 around the old fit, holding 32 factors, 12 iterations and seed fixed. Each variant's new-user inference uses its matching fitting parameters. No future personal ratings enter scores.

## Results

Hit count means at least one top-ten result is a later recorded positive. NDCG also rewards placing positives near the top; it is the registered primary metric. Neither is a probability of enjoying an unreviewed dish.

| Method | People with a hit / 300 | NDCG@10 | Precision@10 | Recall@10 | Unique recommended recipes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Popularity | 97 | 0.06205 | 0.05333 | 0.03205 | 12 |
| Original text centroid | 15 | 0.00570 | 0.00500 | 0.00724 | 951 |
| Original ALS: alpha 20, regularization 1 | 68 | 0.04168 | 0.03067 | 0.02837 | 369 |
| Direct raw co-likes | **99** | **0.06969** | 0.05533 | 0.03843 | 51 |
| Direct normalized/shrunk co-likes | 94 | 0.06446 | 0.04800 | 0.03238 | 291 |
| ALS: alpha 5, regularization 1 | 64 | 0.04132 | 0.03033 | 0.02831 | 236 |
| ALS: alpha 20, regularization 10 | 69 | 0.04349 | 0.03167 | 0.03308 | 363 |
| ALS: alpha 5, regularization 10 | 67 | 0.04236 | 0.03300 | 0.02681 | 231 |

The raw method's gain is modest: two additional people have a hit versus popularity, with a better aggregate placement/recovery score. Raw-minus-popularity NDCG = +0.00765, nominal paired-bootstrap 95% interval [+0.00194, +0.01328]. Normalized-minus-popularity = +0.00242, interval [-0.00827, +0.01377], so its superiority over popularity is inconclusive.

Raw is the provisional nominee under the registered highest-validation-NDCG criterion, not a final-test winner. We have reused validation through several milestones and selected among methods. These intervals are not adjusted for multiple comparisons/selection and do not cover seed variation. The advantage needs the reserved independent evaluation before a stronger generalization claim.

## Does the person's profile add signal?

For every behavioral method we used the same deterministic wrong-person-profile control, retaining each recipient's own earlier-seen exclusions. Correct-minus-shuffled NDCG:

| Method | Difference | Nominal 95% paired interval |
| --- | ---: | --- |
| Direct raw | +0.01375 | [+0.00576, +0.02232] |
| Direct normalized/shrunk | +0.02292 | [+0.01034, +0.03672] |
| Original ALS | +0.01215 | [-0.00046, +0.02522] |
| ALS alpha 5, regularization 1 | +0.00686 | [-0.00712, +0.02101] |
| ALS alpha 20, regularization 10 | +0.01229 | [-0.00110, +0.02648] |
| ALS alpha 5, regularization 10 | +0.00751 | [-0.00679, +0.02221] |

The two direct methods show a positive incremental signal in this control; all four ALS intervals include zero. This supports carrying direct relationships forward for this dataset/task, not a claim that matrix factorization or semantic embeddings inherently fail. It is one profile-shuffle control, not causal separation of taste, exposure, popularity and reviewer activity.

## Popularity and missing evidence remain substantial

Raw co-like ranking is **extremely popularity-heavy**: 99.93% of its top-ten slots are among the fitting top100, versus popularity's 100%. It changes which common dishes appear and their order rather than solving long-tail discovery. Normalized/shrunk is less concentrated (77.60%) and recommends 291 unique items versus raw's 51. That is broader coverage, not independently proven better enjoyment or a measured diversity objective.

Known later rating status across 3,000 slots:

- Raw: 166 higher, eight lower, 2,826 unknown (94.20%).
- Normalized/shrunk: 144 higher, five lower, 2,851 unknown (95.03%).
- Popularity: 160 higher, nine lower, 2,831 unknown.

Observed high-versus-lower AUC on the restricted 92-person subset is raw 0.52180, normalized 0.52227, popularity 0.47692 and original ALS 0.50693. These are near-chance point estimates without AUC uncertainty intervals. They do not establish nuanced dislike prediction or calibrated taste probabilities. Unrated remains unknown; three stars is lower relevance here, not automatically dislike.

## Fixed cases, including the reviewed example

All six pre-existing indices were inspected; no selection by success. Exact top-five entries and seed-specific co-like support are saved locally:

- **0, chicken/fish plus sweets:** both direct methods recover Bourbon Chicken with a recorded later four-star rating. Raw stays with common chicken/roast/spaghetti choices; normalized includes grilled cheese, asparagus, pork chops and garlic bread. Those other results are unknown.
- **60, casseroles/bacon/cookies/Alfredo:** raw produces chicken, roast, pasta and chimichangas, all unknown. Normalized includes a cinnamon brunch cake with a later five-star rating at fourth place.
- **120, Greek food plus pancakes/biscuits:** raw's top five are Bourbon Chicken, Pancakes, Oatmeal Raisin Cookies, Italian Meatballs and Brownies. **Cookies and meatballs have recorded later five-star ratings.** They are cross-category suggestions supported by actual later evidence, unlike the previously inspected unrated CF spaghetti/muffins/Reese's squares. This is one case, not proof all cross-category suggestions are good. Normalized instead includes Bourbon Chicken, green beans, pancakes, cinnamon brunch cake and asparagus, all unknown in this top five.
- **179, seasonings/Mexican-style dishes:** raw stays with common chicken/roast/pasta; normalized includes chimichangas and mashed red potatoes. All inspected results are unknown; neither can be declared successful from food names alone.
- **239, mixed savory and banana desserts:** raw now includes cookies, pancakes and brownies rather than many banana variants. Normalized also includes banana muffins and asparagus. All inspected results remain unknown.
- **299, baking-heavy plus quiche:** raw still puts Bourbon Chicken first and includes pasta/meatballs. Normalized moves cinnamon brunch cake first but retains some savory choices. This is a concrete reason not to claim the raw winner has fully captured this person's apparent baking preference.

Direct case explanations show actual shared-fitting-liker counts, seed/target positive counts and relationship weights for each seed. They support “people who liked this also liked that,” not an invented texture/cuisine explanation or a causal preference claim. Sparse pairs and prolific reviewers can influence these counts.

## Recommendation and stopping point

Stop expanding this grid. The current provisional recommendation is **direct raw item-to-item CF as the primary behavioral ranker**, with popularity as the explicit no-evidence fallback to be specified/tested in later serving work. Retain normalized direct CF as a measured alternative for the product's exploration/coverage trade-off; do not silently switch to it just because its suggestions look more varied.

This remains compatible with a hybrid direction, but its roles should be explicit rather than a forced 50–50 mixture: behavior for preference ranking; content potentially for search/new-item handling. Those content roles are proposals, not newly validated or implemented features. A learned XGBoost combining layer and neural fine-tuning are not supported as automatic next steps by these results. They can be revisited with a specific useful-signal hypothesis and leak-safe labels later.

Recommended next **discussion/approval**: freeze the raw method and its parameters, register a one-time final-test evaluation with fixed baselines, then plan local app integration. Final evaluation should report the frozen method honestly, not become another tuning set. Integration must resolve the 30-dish display catalog versus 5,006 experimental candidates, support for fewer than six likes, empty/no-evidence fallback, actual recipe/photo coverage and truthful explanations. Passing a dish must not become an unverified ingredient/cuisine ban. These are not included in ML 04.

We now have a defensible provisional recommendation foundation, not a validated complete Tasteprint/MealMerge system. October 4 is a reason to finish a clear, honest MVP rather than pursue an open-ended model search; it does not authorize subsequent changes without agreement.

## Verification and reproduction

55 Python tests pass without skips, including eight new pure co-like tests and three new experiment artifact tests. New tests cover exact dense co-like counts, normalization/shrinkage, zero self-links/zero-degree items, binary and duplicate handling, invalid inputs, preserved original artifacts, model alignment, label-independent scores, seen exclusions and complete control accounting. All earlier Python tests remain part of the suite. No package was added; `pip check` passes. Frontend source/dependencies were not changed; no frontend browser/build check was needed for this Python-only milestone.

All three ALS runs have finite, nonincreasing exact objective traces and aligned saved item/user factors. Training objectives with different confidence/regularization are not directly comparable. Fitting times in this environment: raw relationships 7.60 seconds, normalized relationships 10.08 seconds; new ALS runs 103.51, 107.50 and 109.10 seconds. Both direct tables contain 10,062,536 nonzero off-diagonal relationships. Factors, matrices and detailed cases stay in ignored `data/processed/ml04`; published aggregates contain no raw reviewer IDs/names.

All ML 01/02/03 top-level artifact hashes and original baseline metrics reproduce. Final-test rankings remain uncomputed. The experiment protocol enforces unchanged inputs/code; preparation/training verify existing saved artifacts rather than overwrite them. Validation reruns reproduce metrics, controls and provisional selection. The tests verify fitting-user separation through the reused fitting-matrix construction and score invariance when future labels are changed.

```powershell
.\.venv\Scripts\python.exe scripts/run_behavior_comparison.py prepare
.\.venv\Scripts\python.exe scripts/run_behavior_comparison.py train
.\.venv\Scripts\python.exe scripts/run_behavior_comparison.py evaluate
.\.venv\Scripts\python.exe -m unittest discover -s scripts -p 'test_*.py'
```

See [registered choices](ML_04_PROTOCOL.md) and [complete aggregate results/hashes](experiments/ml04-behavior-results.json). This milestone did not repeat the three full-size ALS fits; deterministic small-fixture ALS checks and ML 03's original full reproduction remain evidence, not proof every new fit was rerun.
