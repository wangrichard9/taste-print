# ML 03: collaborative factors help, but the simple hybrid does not

September 30, 2026. This approved milestone trained Tasteprint's first original model using existing ratings. It did not change Discover, onboarding, storage, or the UI. The final test remains unscored; no recommender has been promoted into the app.

## What we built in Tasteprint terms

The model learns a 32-number representation for each recipe from patterns in historical likes—not from recipe wording. When a new person provides liked recipe IDs, we infer their representation while keeping the learned recipe factors fixed, then rank unseen recipes. For evaluation that input is six earlier likes. A local preview command also accepts known-catalog likes and can restrict output to the 30 approved display recipes.

This is collaborative filtering through weighted implicit matrix factorization (ALS). **Collaborative filtering also uses embeddings**; the important distinction is what trained them. Our original MiniLM vectors were reused generic text representations; these new factors were fitted by Tasteprint from recipe/person interactions. A simple percentile-rank blending rule combines content and CF scores for comparison; it is not a trained combining model, XGBoost, or a calibrated probability. The codebase-design skill shaped a separately testable module with fitting, new-user inference and score blending, independent of frontend behavior.

## What data actually supports it?

Same frozen Food.com version-2 inputs and canonical catalog as ML 01:

- 324,955 explicit candidate ratings from 92,830 fitting people. Counts: 262,232 five-star; 43,688 four-star; 10,643 three-star; 4,415 two-star; 3,977 one-star.
- 305,920 unique positive pairs (4–5 stars) from 86,845 people train this first implicit model. Exact star values and 1–3 ratings are not trained as a regression target. Three stars does not automatically mean dislike.
- 61,618 positive-history people have only one candidate like; 25,227 have at least two, 10,103 at least five, and 5,285 at least ten. Median is one; 90th percentile five; 99th percentile 48. Sparse history—not headline dataset size—is a real limitation.
- All 5,006 recipes have at least one positive. The co-like recipe graph has seven connected components: one contains 5,000 recipes and six are isolated single recipes. Connectedness permits information sharing but does not guarantee useful personalized factors.

Our fitting catalog restricts histories to these candidates. These statistics are not the complete source site's histories. They do not establish that a new dataset is necessary; broader interactions already available locally could be a later controlled experiment.

Recorded positives get target one/confidence 21. All other pairs get target zero/confidence one in the fitting objective. This is deliberately weak evidence, **not a claim that every unreviewed recipe is disliked**. Known lower ratings are retained for diagnostics, but this first model does not give them separate training confidence. Recipe popularity, reviewer habits, exposure and heavy users can affect factors; latent dimensions need not be human-readable taste concepts.

## Fair comparison and measured results

All methods rank the same 5,006 candidates, minus each person's earlier seen recipes, for the same 300 held-out validation people. Inputs contain six earlier likes; targets are later recorded 4–5-star recipes. Popularity ranks by fitting-user positive counts without personalization.

“People with a hit” means at least one of the top ten matches a later recorded positive. It is not the percentage of all suggestions a person would enjoy. NDCG@10 also rewards putting these matches nearer the top; larger is better. Precision is the fraction of ten slots with a recorded target; recall is the per-person fraction of later candidate positives recovered.

| Method | People with a hit / 300 | NDCG@10 | Precision@10 | Recall@10 | Unique recipes suggested |
| --- | ---: | ---: | ---: | ---: | ---: |
| Popularity | 97 (32.33%) | 0.06205 | 0.05333 | 0.03205 | 12 |
| Original text centroid | 15 (5.00%) | 0.00570 | 0.00500 | 0.00724 | 951 |
| Collaborative only | 68 (22.67%) | 0.04168 | 0.03067 | 0.02837 | 369 |
| 25% CF / 75% content | 38 (12.67%) | 0.01914 | 0.01533 | 0.01114 | 829 |
| 50% CF / 50% content | 48 (16.00%) | 0.02297 | 0.01867 | 0.01765 | 734 |
| 75% CF / 25% content | 43 (14.33%) | 0.02258 | 0.01767 | 0.01379 | 641 |
| Shuffled CF profiles | 59 (19.67%) | 0.02953 | 0.02767 | 0.01336 | 407 |

No hyperparameters were tuned against these outcomes: one registered 32-factor/12-iteration model, confidence increment 20 and regularization 1, fixed seed. Three blend weights were registered before training. Validation remains exploratory and selecting a blend here would require independent final evaluation later.

Paired 2,000-resample NDCG uncertainty intervals:

- CF minus text: +0.03598, 95% interval [+0.02396, +0.04861]. Behavioral fitting substantially improves recorded-like recovery over this particular text baseline.
- CF minus popularity: -0.02037, interval [-0.03293, -0.00834]. CF still trails popularity on the primary metric.
- 50–50 blend minus CF: -0.01870, interval [-0.03070, -0.00749]. All three registered blends trail CF; none justifies replacing it here.
- Correct CF profiles minus shuffled: +0.01215, interval [-0.00046, +0.02522]. Directionally encouraging, but includes zero. Correct profile assignment has not yet shown a reliable incremental benefit in this one control. CF's improvement over text is not, by itself, proof that nuanced personal taste was learned.

These intervals describe variation across sampled validation people, not uncertainty across training seeds or a multiple-comparison correction. Diversity/coverage is not automatically recommendation quality: CF suggests more different recipes than popularity, but still recovers fewer recorded likes.

## Missing evidence and preference discrimination

Across CF's 3,000 top-ten slots: 92 have a known later high rating, three a known later lower rating, and **2,905 (96.83%) are unknown**. Compare text's 15/0/2,985 and popularity's 160/9/2,831. Unknown must remain unknown, not an invented success or failure in a human taste review.

On the restricted 92-person subset with both future high and lower ratings, macro observed-rating AUC is CF 0.50693, text 0.51581, popularity 0.47692; the 50–50 blend is 0.49632. AUC asks whether a recorded higher-rated recipe scores above a lower-rated one, with half credit for ties. These point estimates are near chance, have no computed uncertainty intervals, and are not the full-catalog ranking task. They **do not support claiming CF now understands fine-grained liking or disliking**.

## All six registered case inspections

Cases were fixed in ML 02 and reused, not selected for a good story. Local snapshots show inputs and top-five outputs for every compared non-shuffled method, with actual later rating status:

- **0, chicken/fish plus sweets:** CF switches to meatloaf, mac and cheese, cookies, spaghetti and pork chops. These are unrated by this person. Popularity recovers recorded positive Bourbon Chicken and banana bread. Cross-category suggestions are not automatically evidence of deeper taste.
- **60, casseroles/bacon/cookies/Alfredo:** CF includes Bourbon Chicken, cookies, banana bread and pulled pork; the blend favors chowders and slow-cooker meals. All inspected top-five results are unrated.
- **120, Greek chicken/potatoes plus biscuits/pancakes:** CF yields spaghetti, Bourbon Chicken, beer bread, muffins and Reese's squares, all unknown. The 50–50 blend includes Buttermilk Pancakes with a known later five-star rating at fifth place. Individual wins can occur despite the blend's aggregate loss.
- **179, seasonings/Mexican-style dishes:** CF includes soup, spaghetti, chicken, dip and sweets; the blend returns taco soup/casserole, chili, butter chicken and salsa. None of the inspected results has a later personal rating.
- **239, mixed savory dishes plus banana desserts:** text and blends concentrate on banana baking variants. CF includes meatloaf, salmon, chicken, banana bread and rolls, reducing that repetition. Every inspected result remains unrated; variety alone does not prove preference success.
- **299, muffins/baking plus quiche:** CF returns apple muffins, oatmeal/gingerbread cookies, carrot cake and brownies, rather than mostly banana/chocolate muffins. Those are all unrated; original text recovers one known five-star muffin that CF's inspected top five misses.

The local CLI preview was also exercised with full-catalog seed recipes while restricting recommendations to 30 display dishes. A baking-heavy profile then gets savory dishes because most baking candidates are absent from the display set. This is a practical integration warning, not a second benchmark: **the 5,006-candidate results must not be presented as validated quality on the 30-dish app catalog**. A human review of actual app choices/output remains pending.

## What this means for the user's hypothesis

The hypothesis is partly supported: recipe resemblance is not the same learning objective as preference prediction, and rating-trained factors outperform our generic semantic baseline on recorded-like recovery. But neither “embeddings inherently do not work” nor “latent CF reliably captures nuanced human taste” follows. Text factors and collaborative factors are both embeddings. This first CF model is substantially better than text, still below popularity, near chance on observed high/lower discrimination, and inconclusive on the shuffled personal-profile control.

Content can still be useful for previously unrated recipes, search, and factual descriptions. Any final hybrid should assign signals roles justified by measured value, not require every component to contribute equally. A learned combiner could downweight weak content; it could also simply learn popularity. XGBoost is not an automatic remedy. Preference-supervised text fine-tuning, direct item-item co-like scoring, different CF confidence/regularization, better onboarding, and more complete interaction coverage are alternatives, not findings from this run or approved follow-on work.

Recommended next **discussion**: a small direct co-like comparator and bounded CF tuning, plus an actual taste review, before a learned combining layer. Direct co-like scoring asks which recipes people who liked the seed recipes also liked, without forcing a low-dimensional model. It gives a useful check on whether factorization/weighting is losing behavioral signal. Avoid another data download without an identified gap. Confirm the next scope with the user before implementing.

References for the algorithm distinction, not evidence of Tasteprint's measured outcomes: [Google matrix factorization](https://developers.google.com/machine-learning/recommendation/collaborative/matrix), [cold start and collaborative limitations](https://developers.google.com/machine-learning/recommendation/collaborative/summary). Reproduction choices are in [ML 03 protocol](ML_03_PROTOCOL.md); complete aggregate values, diagnostics and hashes are in [results](experiments/ml03-collaborative-results.json).

## Verification and reproduction

44 Python tests pass, including 11 new pure tests and three new artifact tests. Checks cover dense least-squares/objective agreement, convergence, deterministic fitting on a fixture, strongly supported synthetic taste groups, empty/unknown input rejection, duplicate likes, blend scaling/ties, seen exclusions, source alignment and unchanged baselines. Mutating future labels does not change any inference scores. No package was added; `pip check` passes. Fitting used CPU/one BLAS thread and took 86.83 seconds in the first run. Objective decreased every iteration from 6,424,336.07 to 3,857,553.99; falling training loss is not a generalization claim.

Model receipt records hashes of aligned float64 item factors (5,006 × 32) and fitting-user factors (86,845 × 32), packages, frozen inputs, exact parameters and code. Validation fold-in never uses those historical user factors. All original ML 01 hashes and baseline metrics reproduce. Detailed cases and factors stay in ignored `data/processed/ml03`; no raw user names/IDs are exported. No frontend source file or dependency was changed in this milestone; frontend build/browser checks were not rerun for this Python-only change.

A second complete training run in the same environment reproduced every user/item factor and every objective value exactly, without modifying saved factors. A second evaluation reproduced all metrics and contrasts exactly. This checks implementation reproducibility, not robustness across other seeds or machines.

```powershell
.\.venv\Scripts\python.exe scripts/run_collaborative_experiment.py prepare
.\.venv\Scripts\python.exe scripts/run_collaborative_experiment.py train
.\.venv\Scripts\python.exe scripts/run_collaborative_experiment.py evaluate
.\.venv\Scripts\python.exe -m unittest discover -s scripts -p 'test_*.py' -v
.\.venv\Scripts\python.exe scripts/run_collaborative_experiment.py recommend --likes 90975,28199,29301,91318,94673,60350 --demo-only --k 5
```

Preparation/training verify existing saved registration/factors instead of overwriting them. Evaluation is validation-only and reproducible; protocol/code changes fail explicitly rather than mix experiments. Out-of-catalog seeds and empty profiles fail explicitly: a production fallback is deliberately not implemented here. No network, key, backend or app setup is required for this experiment.
