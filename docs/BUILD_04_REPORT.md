# Build 04 — real ingredient options

Implemented October 1, 2026, within the separately approved Ingredients scope. No new model fitting, learned ranker, final-test scoring, source download, dependencies or MealMerge engine.

## What a person can do

Enter up to 12 ingredient names, including comma-separated pending input, and find actual recipes across the same 5,006-recipe model catalog. Every result matches at least one ingredient name. Extra ingredients are allowed and shown, not treated as an exclusion. Expand each card to inspect entered-name → original-source-name matches and other listed ingredients. Recipe details open with normal like/pass/save actions and source directions/attribution.

New-to-likes options appear first, 12 at a time; already-liked matches are a separate expandable section, six at a time. All returned matches remain accessible, not a hard three-recipe shortlist. Passed recipes are excluded. Saves stay independent of ranking. Adding a like or pass reranks a submitted list; saving does not. Ingredient edits clear obsolete results and abort pending requests until the next submission. Priority changes rerank the current submitted list. Responses from cancelled requests are ignored, with a ten-second timeout, labeled failure and retry rather than sample matches. No-match results are genuinely empty.

The ingredient list remains page-local, not a persisted pantry. Existing preferences keep the unchanged browser storage key. Requests send ingredients/priority and recipe choices to the local service without persistence or body logging. Source photos still load online. MealMerge and landing/profile illustrative scenes remain samples.

## How matching and ranking work

`scripts/ingredient_matching.py` applies conservative name rules: case/spacing/punctuation normalization, a finite common-plural list, preparation-word removal, a few aliases (e.g. garbanzo beans/chickpeas), and an explicit name-family list (e.g. tomato/cherry tomato). Exact normalized names or those explicit families retrieve candidates. No semantic encoder, substring search, recipe generation or ingredient extraction from dish descriptions is involved. Egg does not match eggplant; rice does not match rice vinegar; milk does not match plant milk or buttermilk. Tomato does not expand to tomato paste/sauce. These limited rules will miss legitimate matches; a family match is not a cooking-substitution guarantee.

Canonical duplicates are removed in input/source lists. Maximum one-to-one assignment between entered names and matching source entries gives the distinct match count: overlapping general/specific names and multiple varieties cannot inflate coverage. Matched source entries are removed from the list of additional entries. These lists lack quantities/units and may be incomplete; counts are ingredient-name coverage, not meal feasibility, purchase quantity, dietary safety or probability of liking.

Ordering is deterministic and hand-authored:

| Priority | First | Second | Third |
| --- | --- | --- | --- |
| A little of both (default) | More distinct ingredient matches | Taste | Fewer other entries |
| Ingredients first | More distinct ingredient matches | Fewer other entries | Taste |
| Taste first | Taste | More distinct ingredient matches | Fewer other entries |

Explicit favorites are identified as known likes, but rendered separately so they cannot crowd the new section. Among new options, positive average raw shared-liker scores lead; when there is no shared-like evidence, fitting-data popularity is the fallback. Final ties use source recipe ID. Explanations show a real strongest shared-like connection or identify popularity fallback, never inferred profile tags or invented percentages. The frozen co-like scorer and original Discover ordering remain unchanged and their equivalence checks still pass.

This composes ingredient retrieval with existing preference ranking; it is **not** a newly trained semantic/CF hybrid or proof of improved niche discovery. “New” means not recorded as liked by this local profile. Earlier popularity concentration and quality limitations still apply. Ingredient ranking has not received a separate relevance benchmark or user usability evaluation.

## Verification

- Full Python suite: **71 passing tests**, including nine new ingredient tests, preserved serving/model checks and frozen-artifact provenance. Covers aliases/plurals, processed-product/substrings, source/input duplicates, overlapping-name coverage, all priority orders, known favorites, passes, popularity/evidence, invalid requests, real source metadata and HTTP access/errors.
- Frontend suite: **39 passing tests with the live test enabled**. Normal runs have 38 passing plus one skipped opt-in live check. Covers input limits/draft combination, response/source-evidence validation, favorites/new split, bounded static card rendering, no-match presentation, request cancellation/stale responses, edit/unmount cleanup, timeout, retry, invalid-request versus disconnected-service feedback and likes-versus-saves. Lifecycle tests use a hook harness, not React DOM/browser automation; presentation tests render static HTML.
- The opt-in test calls `/api/ingredients` through Vite for all three priorities with the six real onboarding likes and one pass, then runs the production frontend decoder over every result.
- Live smoke check: tomatoes/spinach/chickpeas with that specific six-like/one-pass fixture yielded **400 new options and two matching favorites**. Balanced first new option was Sweet Potato Curry With Spinach and Chickpeas (three matches, 11 other listed entries). Ingredients first promoted Chickpea and Fresh Tomato Toss among two-match results. Taste first led with Jo Mama's World Famous Spaghetti (one match, 14 other listed entries). These are runtime checks of priorities, not measured recommendation-quality results or the user's actual opinions.
- A separate single-like/source-ingredient request retained its known favorite alongside 586 new options. Original source names/details and model catalog size remained intact; `/api/health` reports `testScored: false`.
- TypeScript/production build passes. Main bundle remains about 5.15 MB minified / 774 KB gzip because source summaries are bundled. Vite's large-chunk warning remains; no bundle redesign was included.

Initial full Python runs exposed Windows connection resets when rejecting POST requests with unread bodies. The service now consumes a size-bounded body with a read timeout before origin/type/path rejection, without parsing or scoring unauthorized requests. Access restrictions and size limits remain intact. The full suite passed after the correction; the local service was restarted with the final code.

Interactive browser navigation, pointer/keyboard behavior, persistence refresh and laptop/narrow layout review remain **pending**: the earlier browser error tabs were blocked by the browser tool's URL policy. No alternate surface was used to bypass that restriction. API, decoder, lifecycle/static checks and build are not substitutes for that review.

## Reproduce and review

Run `npm run dev:all` with the existing environment/artifacts. Open Ingredients, try tomatoes/spinach/chickpeas, compare priorities, expand ingredient details and open a recipe. Confirm whether new options versus known favorites and the extra-ingredient burden feel right. User review should precede changing ranking policy or beginning a group engine.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s scripts -p "test_*.py"
npm test
npm run build
# With Vite and the local model running:
$env:VITE_TASTEPRINT_LIVE_TEST = '1'
npm test
Remove-Item Env:VITE_TASTEPRINT_LIVE_TEST
```

Next proposal: discuss a bounded real MealMerge group-ranking scope, using the existing individual scores with an explicit compromise objective. No such engine, fairness rule or final-test evaluation is approved by this milestone.
