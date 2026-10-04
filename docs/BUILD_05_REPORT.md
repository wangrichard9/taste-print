# Build 05 — real local MealMerge

Implemented within the approved current-profile plus 1–3 local-guests scope. The user's positive Ingredients review preceded approval; it is individual product feedback, not model-quality evidence. No source/model download, new dependency, training, learned hybrid/ranker, ingredient/group safety engine or final-test scoring.

## Working experience

MealMerge uses the current Tasteprint automatically and starts with one empty Guest 1, not authored Alex/Maya opinions. People can take turns on the laptop: edit a guest's name, like/pass/clear real recipes and inspect original ingredient/source links. Guest browsing starts with the 30 reviewed recipes; all 5,006 model recipes and recorded-choice views are searchable and bounded to 12 cards initially. Same-opinion clicks clear that choice. Add up to three guests, clear a guest's choices or remove the guest and their record. Personal choices are edited through Your Tasteprint, never reassigned from guests.

Guest edits save immediately to `tasteprint:mealmerge:foodcom:v2`. The personal record remains `tasteprint:local:foodcom:v2`. Names can be temporarily blank while typing; a fallback guest name is used for storage/requests. Storage/read failures are labeled. Guest/table edits clear obsolete results and require Find shared recipes again; priority changes and personal opinion changes rerank a submitted table. Saves do not drive ranking. Loading, invalid profiles, service errors, timeouts and retry never turn into sample picks. Cancelled/obsolete responses are ignored.

Real group options replace fixed fixtures. Cards show 12 at a time with all remaining eligible recipes accessible through Show more. Already-liked recipes remain eligible; any participant's pass excludes that recipe, not all its ingredients. Results distinguish known likes, actual shared-like evidence, unknown members and pure-popularity fallback. A per-person evidence table exposes positions and historical shared-liker connections. Real result details use source directions/attribution and normal personal like/pass/save actions; these never edit a guest. Photos remain online and may be missing. Landing/profile sample scenes remain separate, labeled illustrations.

## Group policy, exactly

Reuse the unchanged raw co-like scorer: average historical shared-liker counts across unique model-supported likes, with zero self-links. No new learning or final evaluation occurs. Each person's positive recipes, excluding their own likes/passes, define their personal positive recommendation pool. For a positive score, position is one plus the number of recipes with a strictly higher score; equal scores share a position. Normalize to `1 - (position - 1) / positive_pool_size`. An explicit like uses internal value 1, a known preference rather than a guessed probability. A recipe without explicit/shared-like evidence uses missing (`NaN`), not 0 or a dislike.

Reject recipes passed by anyone. For each remaining recipe, count members with known/shared-like evidence and aggregate only their supported relative values. Both modes first maximize this evidence coverage:

- **Balanced compromise (default):** weakest supported relative value first, average second.
- **Overall appeal:** average supported relative value first, weakest second.

Training popularity breaks remaining ties, then source ID. Aggregate comparisons round to 12 decimal places to avoid false differences between mathematically tied rank fractions. Compensated sums also keep member display order from affecting the average. When no member has evidence for a recipe, order it by labeled popularity after evidenced options. With no personal evidence anywhere, both modes fall back to popularity. A blank guest contributes no value and therefore cannot shuffle order or act like a dislike; the coverage/unknown labels still reflect that extra member.

This is a disclosed heuristic over recommendation positions, **not calibrated satisfaction, a validated fairness guarantee or improved preference learning**. Broader evidence can favor frequently rated recipes, reinforcing existing popularity concentration. Ranking within a personal pool discards score magnitude and does not resolve missing-label bias. Different/identical profiles may produce different/identical priority orders. Guest likes of plant-forward dishes are not a vegetarian constraint. Group outputs include desserts and other recipe categories; there is no main-meal classifier. Historical individual ranking metrics do not validate group enjoyment or usability.

## Checks and outcomes

- **83 Python tests pass**, including 12 new group/startup checks. Covers tie-aware normalization, scale/member-order invariance, duplicate likes, policy trade-offs, known/unknown/empty pools, explicit pass conflicts, whole-table validation, sparse/dense score/evidence equivalence, real saved-model evidence and HTTP restrictions. Earlier Discover/Ingredients and frozen provenance checks pass unchanged.
- **62 frontend tests pass with both live checks enabled**; normal runs have 60 passing plus two opt-in live-server skips. Covers guest identity/name limits, opinion toggling and isolation, separate storage including corrupt/blocked storage, complete group-response validation, real shared-like positions/seeds, passes, no-match/fallback states, bounded static guest/results rendering, request replacement/cancellation/timeout/retry, resubmitting an edited table and saves versus likes. Lifecycle/storage tests use a hook harness, not browser interaction. Static HTML does not prove layout or keyboard behavior.
- The opt-in MealMerge test requests both priorities through the running Vite proxy, decodes every returned recipe with the production frontend validator, then adds a blank guest and confirms all positions/order remain unchanged while that guest's evidence is unknown. The prior live Ingredients check still passes.
- A disclosed smoke fixture uses the six existing starter recipes as one person's likes; the guest likes Greek chickpeas & spinach, Roasted cauliflower & garlic, Black beans & rice and Chickpea curry, and passes Garlic & herb baked salmon. **5,005 recipes remain**, one excluded; two people have evidence, and 133 entries have no personal evidence and use popularity fallback. These are fixture choices, not the user's actual profile or historical group labels.
- Both priorities lead with Bourbon Chicken, Creamy Cajun Chicken Pasta and Oatmeal Raisin Cookies in that fixture. Balanced next favors Kittencal's Italian Melt-In-Your-Mouth Meatballs (personal positions 8/8); Overall instead promotes Greek Potatoes (12/4). This demonstrates a calculable trade-off, not a guarantee the people would enjoy those dishes. The underlying popularity bias remains visible rather than hidden.
- TypeScript and production build pass. Main bundle remains about **5.16 MB minified / 777 KB gzip**; the existing large-chunk warning remains. Source summaries are still bundled and no unrelated optimization was included.

Live checks initially encountered an older service answering 404 for the new endpoint, then a startup-time timeout. Process inspection verified two recipe-service instances launched from this project's virtual environment. Only those scoped service processes were stopped; the associated old combined launcher also stopped Vite, which was restarted. The final model service now uses an exclusive Windows port bind, and a test verifies that a second server cannot claim a served port. Health identifies `build05` and its three features. After both services responded, all live checks passed. The final test remains unscored.

Automated interactive browser navigation, pointer/keyboard flow, refresh persistence and laptop/narrow visual checks remain **pending** under the existing error-tab URL-policy limitation. No alternate browser surface was used to bypass it. The user's earlier Ingredients review is not browser verification of this new feature.

## Try and discuss next

The local preview/model are running. Refresh if needed, open MealMerge, name Guest 1 and give that guest several genuine likes. Find shared recipes, compare both priorities and inspect Per-person evidence. Add/change another guest to judge whether the trade-offs feel understandable. Guest deletion/clearing affects only that guest's record; clearing site data can erase all local records.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s scripts -p "test_*.py"
npm test
npm run build
# With the model and Vite running:
$env:VITE_TASTEPRINT_LIVE_TEST = '1'
npm test
Remove-Item Env:VITE_TASTEPRINT_LIVE_TEST
```

Next proposal, not started: review an end-to-end Expo demonstration and agree on the final evidence/evaluation scope. Independent final-test scoring, ranking-policy changes and additional UI polish require their own discussion/approval.
