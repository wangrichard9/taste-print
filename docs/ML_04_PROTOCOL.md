# ML 04: bounded comparison to choose a behavioral foundation

Registered September 30, 2026 before fitting/scoring. The user approved direct co-like comparison and bounded CF tuning, reviewed suggestions first, then asked to continue toward a final approach. This is not approval for app integration or a learned ranker.

## Frozen task and inputs

Use ML 01's 5,006 canonical candidates, fitting-user 4–5 likes, 300 validation profiles with six earlier likes, earlier-seen exclusions and later 4–5 relevance. Reuse ML 02 reconstructed histories and ML 03 model/score logic without modifying any old files. Hash every top-level artifact in ML 01/02/03, registered protocol and implementation. Reserved final-test rankings remain uncomputed. No download or added dependency. The rating task remains user-disjoint, not globally chronological.

The five top CF suggestions in the reviewed profile are among the 76 most popular candidates. That motivates controlling commonness, not a finding that popularity causes every recommendation. The user's safe-spaghetti/uncertain-muffin/surprising-Reese's reactions are qualitative plausibility feedback, not actual preference labels for the historical reviewer.

## Fixed methods; no result-driven additions

1. Original popularity, original full-text centroid, and original ML 03 ALS (32 factors, confidence increment 20, regularization 1, 12 iterations) remain comparisons.
2. **Direct/raw:** binary fitting matrix R; C=R.T R counts fitting people who liked both items. Zero the diagonal. A new user's score is the mean of C rows for their unique seed likes. No negative inference from unseen pairs.
3. **Direct/cosine_shrunk:** for i != j, weight = `C_ij / sqrt(n_i*n_j) * C_ij/(C_ij+10)`, where n is fitting-positive item count. Zero diagonal and zero support yields zero. The first term normalizes item commonness; the second discounts links based on few shared people. This is not a causal deconfounding guarantee or a learned probability. Average six seed rows. Keep all edges: no neighbor-count parameter or tuning of shrinkage.
4. Three new ALS configurations with factors/iterations/seed unchanged: (alpha=5, lambda=1), (alpha=20, lambda=10), (alpha=5, lambda=10). Together with the old model they form a 2×2 grid; confidence 1+alpha applies to positives, weak zero-target confidence one to all other pairs. Train and fold in using each model's matching parameters. Save separate aligned factors/objective traces. No dimension/iteration grid and no encoder retraining.

Fit-only: matrices, counts, relationship weights and factors. Validation six likes inform new-user scores; validation later labels inform only evaluation/selection. Historical fitting user factors are never used for validation people. Old baselines and their exact metrics must reproduce.

## Evaluation and diagnostics

Primary macro NDCG@10; also precision/recall/hit@10, unique candidates, known high/lower/unknown slots, restricted observed-rating AUC. For every behavioral method (six including original ALS), use the same single fixed derangement of seed profiles while retaining recipient exclusions. Report paired 2,000-bootstrap NDCG intervals versus popularity, original ALS, and each method's shuffled control. Report top-ten share in fitting top100 to describe popularity concentration, not to reward obscurity.

Inspect all six fixed cases 0, 60, 120, 179, 239, 299, not selected successes. For direct normalized recommendations retain seed-specific support count, seed/target positive counts and actual relationship contribution; factual co-like explanations are available, but are not ingredient/taste causal explanations. Keep snapshots local and detailed profile keys out of published aggregates.

## Stopping and selection

Report every registered method, no extra blend/grid after seeing outcomes. Nominate the behavioral method with highest validation NDCG@10 (ties within 1e-12 use method-name order); this is provisional selection, not an independent final-test winner. Evidence for personalized value additionally requires examining correct-vs-shuffled and popularity contrasts. A better point estimate with an interval including zero is inconclusive. Multiple comparisons and repeated use of the same validation set create optimism; bootstrap intervals do not correct this or training-seed variability.

At the end, recommend a bounded product approach or state the remaining specific uncertainty. Do not claim we now have a validated final hybrid. Content may remain useful for unrated-item fallback/search; neither role is implemented here. XGBoost needs demonstrable useful inputs and a leak-safe training protocol; it is not added automatically. Discuss final evaluation and app candidate/onboarding integration with the user before implementing them. The 30-dish frontend and 5,006-candidate evaluation are distinct.

## Verification

Dense-fixture co-like counts and normalization/shrinkage; no self-links; duplicate likes; empty/unknown/nonfinite input handling; zero-degree item; popularity normalization vs raw count; scores independent of future labels; seen exclusion and fitting-only inputs. Validate factor shapes, finite values and nonincreasing exact objectives. Record packages, runtime, seeds and all artifact/code hashes. Re-run all Python tests and cached evaluation for exact metric reproduction. No UI changes or frontend build required for this Python-only milestone.
