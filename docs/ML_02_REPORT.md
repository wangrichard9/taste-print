# ML 02: what the bounded content experiment found

Completed September 30, 2026 local time. The [registered protocol](ML_02_PROTOCOL.md) fixes the original 300 validation people, six earlier likes, 5,006 candidates, labels, exclusions, model revision and metrics. All six registered text/profile variants were run. ML 01 files remain byte-for-byte unchanged. Final-test rankings remain uncomputed. No new source/model download, dependency, neural training, collaborative model, backend, or app change was added.

## Outcome: no simple content fix closes the gap

An ingredient-only representation and preserving individual likes produce modest changes, not a reliable solution. Primary metric is NDCG@10, which rewards recorded later likes nearer the top. Hit count is the number of people with at least one recorded later like in ten results, not actual satisfaction.

| Recipe text | Profile rule | People with a hit / 300 | NDCG@10 |
| --- | --- | ---: | ---: |
| Original full text | Average profile | 15 | 0.00570 |
| Original full text | Closest liked recipe | 18 | 0.00652 |
| Original full text | Two closest liked recipes | 19 | 0.00673 |
| Ingredient names only | Average profile | 22 | 0.00947 |
| Ingredient names only | Closest liked recipe | 22 | 0.00829 |
| Ingredient names only | Two closest liked recipes | 21 | 0.00961 |
| Fitting-user popularity | Not personalized | 97 | 0.06205 |

Every changed content variant's paired 95% bootstrap interval for NDCG improvement over the original includes zero. Ingredient/top-two has the highest observed content NDCG, but its difference of +0.00392 has interval [-0.00136, +0.00949]. These exploratory validation comparisons do not establish a dependable winner; no correction for multiple comparisons was made. Changing text and profile rules alters different aspects of ranking; there is no reason to claim a single improved number is a solved recommendation model.

## What we can support

### 1. The tested mechanical explanations were not found

Original semantic and popularity metrics reproduce exactly. Rebuilding all 300 people's canonical raw histories reproduces their six seeds, timestamps, seen exclusions and target IDs. Eight seeded, re-encoded full-text recipe rows agree with frozen vectors (maximum element difference about 7.31e-8). Both representations fit within the model limit: full maximum 197 tokens; ingredient maximum 120; no truncation. Vectors are finite, normalized, and source-ID aligned. These checks reduce concern about those implementation errors; they do not prove the absence of every possible bug or validate every source ingredient list.

### 2. Averaging interests and mixed text are not sufficient explanations

Closest/top-two scoring preserves separate liked dishes, but only lifts full-text hit counts from 15 to 18/19. Ingredient text gives 21/22 hits; removing title/category/keywords together does not identify which field matters. Changes are uncertain and remain far below popularity. Averaging all six seed-to-candidate cosine values is proportional to original centroid scoring, so it is not a separate experimental alternative; this is covered by a test.

### 3. Exact recorded likes are extremely incomplete evidence

Across the original content method's 3,000 recommendation slots: 15 have a known later 4–5-star rating, 0 a known later 1–3-star rating, and **2,985 (99.5%) have no later rating** from that person. Popularity has 160 known higher, 9 known lower, and 2,831 unknown. Unrated recipes could be enjoyed or disliked; the experiment cannot tell. This does not justify relabeling unknown results as successes or explain away popularity's stronger recovery of recorded likes.

The 300 people's full usable-content histories contain 32,288 later positive records, of which 6,650 are in this catalog: **20.60% pooled coverage**. Averaging coverage equally across people yields 50.00%, because very prolific reviewers contribute disproportionately to the pooled count. This differs from ML 01's 27.49% population-wide candidate coverage: here the denominator is specifically these 300 people's positive records after their seed cutoff. Both methods face the same catalog restriction; it cannot by itself explain their relative gap. The rest of those source recipes already exist locally—another dataset is not automatically necessary to expand candidates. More candidates would also make ranking harder.

### 4. Strong personal-preference signal has not been demonstrated

Using other people's six-like profiles through one fixed shuffle recovers a later like for 13 people, versus 15 with their correct profiles. The shuffled-minus-correct NDCG difference is -0.00107, interval [-0.00528, +0.00310]. This one control is inconclusive; it does not prove personal choices never matter.

For 92 people who have both later 4–5-star and later 1–3-star ratings, the original scores put a randomly paired higher-rated recipe above a lower-rated one 51.58% of the time (macro AUC 0.516). Full/top-two reaches 0.536; ingredient methods range 0.442–0.470; popularity is 0.477. This narrow, selection-biased diagnostic is near chance numerically and does not rescue the embedding approach as a strong liking predictor. No uncertainty interval was computed for these AUCs; they are not substitutes for the all-candidate ranking results. Three stars is treated as lower relevance, not necessarily dislike.

## Fixed case inspection

All six registered profile indices were inspected, not chosen for success. Cases show multiple behaviors, so no claim that all misses are sensible:

- Profile 120 likes biscuits/pancakes plus Greek chicken/potatoes. Full/closest returns Greek potatoes, souvlaki marinade and biscuits, where original averaging returns mostly fried/breaded chicken. This illustrates preserved interests, but those alternatives are unrated—not established successes.
- Profile 239's top results repeatedly include banana bread variants, despite six likes covering potatoes, burgers, chicken, desserts and banana bread. Matching individual recipes can become near-duplicate repetition rather than broad preference discovery. Conservative exact-identity deduplication does not remove these variants.
- Profile 0's ingredient-only/closest suggests pork chops alongside chicken and tortilla dishes; ingredient/top-two includes a seasoning blend. Shared ingredients need not imply the same main food or an appropriate meal. The snapshot labels every suggestion as known higher/lower/unknown; apparent similarity is not a liking label.
- Profile 299 has a recorded positive banana/chocolate muffin among original recommendations, while many similar baking alternatives remain unrated. Exact-ID recovery can miss plausible related recipes without proving they are good.

The closest-seed/shared-ingredient annotations in the case file always use **original full-text** similarities as a common descriptive reference, not each variant's explanation or proof of its scoring cause. Exact ingredient-name overlap misses synonyms. Detailed local cases contain no raw user IDs/names, and remain in ignored processed data.

## Does this mean more data is needed?

Not established. We already have substantial local recipe/rating data, but this simple generic encoder was not trained to predict liking. The experiment identifies an **objective/evidence mismatch**: food resemblance, exact historical recipe recovery, and actual enjoyment are different questions. Representation changes alone did not solve the measured task, and missing ratings limit what that task says about actual enjoyment. This is an evidence-backed diagnosis of limitations, not proof of one sole causal root.

Recommended next discussion: retain these content methods as comparisons; train a preference-aware collaborative/hybrid model on existing fitting ratings and explicitly handle new-user seed choices. Complement exact-history metrics with a small real-person review of recommendations, keeping subjective feedback clearly separate from quantitative held-out results. A larger candidate catalog, another encoder, neural fine-tuning, or extra data should be a deliberate next experiment with a stated reason, not an automatic response to this result. No production content-method replacement has been approved.

## Verification and reproduction

30 Python tests pass against local artifacts, including nine pure ablation tests and three ablation integration checks. The original 18 tests remain green. New tests cover genuinely different profile rules, average-cosine equivalence, deterministic profile shuffling, observed-rating AUC/ties, unknown rating status, grid completion, baseline preservation and label accounting. Source hash verification and history reconstruction are enforced at runtime. Neural weights are reused, not fine-tuned. This milestone changes no frontend files; the current frontend's 12 tests and production build were rerun and pass. Cached reruns reproduce all metrics exactly, with original ML 01 hashes still unchanged.

```powershell
.\.venv\Scripts\python.exe scripts/run_content_ablation.py prepare
.\.venv\Scripts\python.exe scripts/run_content_ablation.py encode
.\.venv\Scripts\python.exe scripts/run_content_ablation.py evaluate
.\.venv\Scripts\python.exe -m unittest discover -s scripts -p 'test_*.py' -v
```

Preparation registers choices before scoring and verifies, rather than replaces, an existing protocol. Encoding is offline and reuses the ML 01 model cache. It freezes a new ingredient vector file in `data/processed/ml02`; reruns verify cached vectors and raw-history receipts. Original file hashes are checked before/after. Aggregate evidence is published in `docs/experiments/ml02-content-results.json`; detailed histories/rankings stay local. The diagnosis skill shaped this work into fixed probes and reproducible comparisons; bug-fix phases were not applied because no implementation bug was established, and the poor original benchmark result is deliberately preserved.
