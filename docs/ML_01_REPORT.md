# ML 01 measured result

Completed September 30, 2026 local time, following the approved [ML 01 protocol](ML_01_PROTOCOL.md). This implements content ranking outside the app, not a finished hybrid. Tasteprint reuses MiniLM weights; no neural fine-tuning, collaborative training, or XGBoost training occurred.

## Outcome

The semantic recommender produces profile-dependent unseen-recipe rankings, but **does not beat popularity on this validation task**. This result is retained without changing the protocol/model/text after seeing scores. Test rankings remain uncomputed.

300 held-out people, six earlier liked recipes each, 5,006 candidates, ten recommendations, all observed pre-cutoff recipes excluded. Each person has an average 22.17 recorded later positive recipes within the catalog. Both methods use identical profiles, candidates, relevance rules, and exclusions.

| Measure | Popularity | Semantic embeddings |
| --- | ---: | ---: |
| People with a withheld like in top ten | 97 / 300 | 15 / 300 |
| HitRate@10 | 32.33% | 5.00% |
| Precision@10 | 5.33% | 0.50% |
| Recall@10 | 3.20% | 0.72% |
| NDCG@10 | 0.06205 | 0.00570 |
| Candidate coverage across recommendations | 0.24% (12 recipes) | 19.00% (951 recipes) |

NDCG rewards correct recipes nearer the top. Semantic-minus-popularity NDCG is -0.05635, with a paired 2,000-resample validation bootstrap interval [-0.07001, -0.04366]. Semantic scored higher for 7 people, popularity higher for 97, with 196 tied. These are sample-specific retrieval measures, not liking probabilities or final-test results.

## Data and reproduction evidence

- Content checks accept 520,298 source recipes and collapse 2,740 conservative exact name/ingredient duplicates. 81,421 review rows are excluded for invalid/unjoined/incomplete/non-explicit records; 64 user/content repeats collapse to their earliest valid rating.
- Before candidate filtering, user partitions contain 187,453 fitting, 23,515 validation, and 23,153 test people. No evaluation person contributes to popularity. The selected fitting artifact contains 324,955 ratings from 92,830 people.
- Candidates are the 5,000 fitting-popular content identities plus approved demo identities; overlap gives 5,006 recipes. Validation candidate positives cover 38,328 / 139,418 positive records, approximately 27.49%.
- Validation has 902 qualifying profiles (approximately 3.84% of its people); 300 are selected deterministically. Test has 936 qualifying profiles; 300 are reserved. This is a catalog-conditioned active-reviewer experiment, not a representative sample of Expo visitors.
- MiniLM revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`: four CPU threads, batch 32, normalized 384-dimensional vectors. Loading/encoding took approximately 130 seconds. Maximum input length was 197 tokens; none exceeded the 256-token limit.
- Python 3.12.14; NumPy 2.5.3; CPU PyTorch 2.14.1; SentenceTransformers 6.1.0; Transformers 5.18.0; PyArrow 25.0.1. Full environment pins are in `requirements-ml.txt`; `pip check` passes.

Frozen profiles, fitting ratings, source texts, vector/protocol hashes, and source receipts remain under ignored `data/processed/ml01`. Aggregate result/provenance snapshots are in `docs/experiments/`; these contain no historical names, review text, or user profiles. See the protocol for commands and metric definitions. Original bulk source hashes are also recorded in the data audit.

## Verification and smoke checks

18 Python tests pass, including known metric fixtures, stable ranking ties, seed/seen exclusion, timestamp tie handling, exact identity, source-text isolation, user partition isolation, artifact hashes, training-only popularity recount, and vector provenance/normalization. Integration tests skip on a clean checkout until local artifacts exist; all passed against this run. Existing frontend tests: 12 pass. Production build: passes. Reusing frozen vectors and rerunning validation produces identical metrics without downloading/loading the model.

Illustrative two-like CLI checks (not evaluation results): Greek salad + baked salmon first recommends Greek chickpeas/spinach and grilled salmon within the approved display catalog. Macaroni/cheese + mushroom/garlic linguine instead first recommends Mexican pasta salad and cucumber/cilantro pasta salad. The latter illustrates that generic pasta similarity may miss the intended creamy/comfort preference. Seed dishes are excluded. UI, browser storage, and recipe selection remain unchanged.

## Interpretation and next discussion

This benchmark rewards exact historically reviewed IDs, not general food resemblance. Popularity-based candidates and positive-heavy self-selected reviews favor popularity; the generic encoder and simple mean profile may lose taste distinctions. These are possible explanations, not diagnosed causes. Unreviewed recipes may still be liked. The split is user-disjoint, not globally chronological; near-duplicate variants may remain.

Popularity recovers more recorded likes but recommends only 12 recipes across this group. Semantic recommendations vary more widely but recover fewer recorded likes. Diversity is not accuracy, and these results do not establish a satisfying visitor experience.

Next **unapproved** scope to discuss: train collaborative filtering, explicitly handle how new people's choices connect to learned recipe factors, and compare a simple hybrid. XGBoost remains a subsequent learned-ranking candidate, not a promised improvement or abandoned requirement. App integration, custom dishes/ingredient extraction, and MealMerge need separate agreements.
