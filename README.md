# Tasteprint

Working name for a personalized food recommendation project for the IgniteAI Expo Data Science track.

The product learns from recipe data and people's interactions, then uses one preference model for food discovery, ingredient-aware ranking, and group recommendations through MealMerge.

## Current stage

Build 05: a laptop-first React/TypeScript app with white-and-cobalt styling and **5,006 real Food.com recipes**, connected to the saved raw co-like model through a loopback-only Python service. Discover, Ingredients and MealMerge now use real recipe results. Includes ingredient/name search, local favorites, source directions/attribution, six-recipe onboarding using the adapted React Bits Stepper, and editable browser-local MealMerge guests. Your Tasteprint still describes explicit choices; landing/profile demonstration scenes remain clearly labeled examples.

All 30 manually reviewed recipes are preserved within the model catalog; the other 4,976 are bulk source metadata, not manually reviewed. Their single category tag is source-provided, not an inferred taste trait. Source directions for bulk records load on demand; photos remain remote and can fail. Discover ranks unseen dishes from explicit likes, then labels popularity fallback where shared-like evidence is absent. Saves do not affect ranking, passes exclude only that recipe, and service failure is labeled catalog order—not fake personalization. Amounts/units are not invented; consult the original recipe before cooking. Ingredients are not allergy guidance. This is a local temporary demo, not a public launch.

ML 01 compared recommendations from six earlier likes against popularity across 5,006 recipes and 300 validation people. Embeddings alone underperformed popularity. See the [measured report](docs/ML_01_REPORT.md) and [frozen protocol/reproduction commands](docs/ML_01_PROTOCOL.md). That milestone left the final test unscored; the separately approved ML 05 result below is now authoritative. Build 03 did not rerun or tune these experiments.

ML 02 tests six content-text/profile variants on that unchanged validation task and inspects missing ratings and source-history coverage. Gains are modest and uncertain; no content method was promoted into the app. See the [diagnosis and reproduction commands](docs/ML_02_REPORT.md) and [registered comparisons](docs/ML_02_PROTOCOL.md). The original baseline files remain unchanged.

ML 03 trains 32-dimensional collaborative factors from existing fitting-user likes and infers a new person's vector from their earlier choices. CF recovers a later like for 68/300 validation people, versus text's 15 and popularity's 97. Three simple content/CF blends trail CF; no app method was changed in that milestone. See the [measured findings, limitations and local preview commands](docs/ML_03_REPORT.md) and [registered protocol](docs/ML_03_PROTOCOL.md). ML 03 left final-test rankings uncomputed.

ML 04 compares direct co-like methods with bounded ALS variants. Raw co-like ranking has validation NDCG@10 0.06969 versus popularity 0.06205, with hits for 99/300 versus 97. Correct-profile assignment adds signal in the fixed shuffle control, but this reused-validation selection remains popularity-heavy and does not establish nuanced taste prediction. See the [measured comparison](docs/ML_04_REPORT.md). The user separately approved Build 03 app integration October 1 and ML 05 final evaluation October 2.

**ML 05 final test is complete:** without retraining or changing the app, frozen raw co-like ranking has NDCG@10 **0.07202** versus popularity **0.05886**, with a later recorded like recovered for **107/300** people versus **84/300**. The paired improvement interval and correct-versus-shuffled interval are positive. Discovery remains limited: **55 distinct recipes**, with **99.6%** of top-ten slots in the fitting top 100. Existing Discover top tens match the benchmark for all 300 test profiles. See [final findings and verification](docs/ML_05_REPORT.md), [registered rules](docs/ML_05_PROTOCOL.md), and [plain-language Expo explanation](docs/EXPO_ML_EVIDENCE.md). These are individual historical ranking results, not validation of ingredient usability, group satisfaction, sensory graphics or liking probabilities. ML 01–04 artifacts remain unchanged.

Audit the completed final receipt without rescoring: `.\.venv\Scripts\python.exe scripts/run_final_evaluation.py verify`. The write-once evaluation refuses a second run; do not delete its marker or tune against the test.

## Run locally

Requires Node.js 22.12+ on the Node 22 line (tested with 22.14.0).

```sh
npm ci
npm run dev:all
```

Open http://127.0.0.1:5173/#discover. `dev:all` starts Vite and the local model together; Ctrl+C stops the child processes it started. Requires the project `.venv`, saved ML 01/04 artifacts, and exported Discover metadata already present in this workspace. No API key or cloud service is needed. To run separately, use `npm run dev:model` in one terminal and `npm run dev` in another. Model binds only `127.0.0.1:8000`; Vite proxies `/api`. Production browser preview is `npm run build` followed by `npm run preview`, with the model running separately.

If the development page is blank and React startup requests return `504 Outdated Optimize Dep`, stop Vite, run `npm run dev -- --force`, then reload the browser. This rebuilds Vite's generated dependency cache without changing preferences or model artifacts. Use the configured preview port **4173**: the backend permits the app origins on 5173 and 4173, so a preview on 5174 receives a 403 for browser model requests.

To regenerate the expanded source catalog from **existing frozen artifacts and downloaded recipes** (not train a new model):

```powershell
.\.venv\Scripts\python.exe scripts/export_discover.py
```

Raw data and saved model artifacts remain ignored/local; a fresh checkout with only npm dependencies cannot reproduce personalized ranking. For the Python packages use the project environment and `requirements-ml.txt`; the earlier ML reports explain original fitting. If the model is stopped, the app still lets you browse, save and record choices, but explicitly labels ranking as unavailable. Verify with `npm test`, `npm run build`, and `.\.venv\Scripts\python.exe -m unittest discover -s scripts -p "test_*.py"`.

Preferences and favorites use this browser's localStorage. The local service receives recipe likes/passes for scoring, ingredients/priority for ingredient matching, and member IDs/names/choices/priority for MealMerge; it does not persist them, log request bodies, or expose historical people. Ingredients are page-local: leaving the page clears the list, not your saved preferences. MealMerge guests persist separately under `tasteprint:mealmerge:foodcom:v2`, never the personal `tasteprint:local:foodcom:v2` record. There are no accounts, invitations, telemetry, or cloud sync. Photo requests still go to Food.com's image CDN; offline caching is not a priority. The old sample profile is untouched. Changing origin/browser creates separate profiles. Clearing site data may erase choices and guests.

## Try the current build

For the October 4 demo, follow the [short startup, recovery and rehearsal guide](docs/DEMO_GUIDE.md). After the app/model are ready, run `.\.venv\Scripts\python.exe scripts/check_demo.py` from the project folder. It checks six real local flows without saving choices, training or rescoring the final test; it fails nonzero if a check is unavailable or invalid. For an already-running production preview, pass `--base-url http://127.0.0.1:4173`. Keep the same browser origin for your actual saved profile. See [Demo 01 verification and limitations](docs/DEMO_01_REPORT.md), including the initial live-check timeout and later passing checks. No reliability guarantee or new algorithm is claimed.

1. Search an ingredient such as basil, change filters, and save a dish.
2. Select **Refine your taste**, give at least two dishes an opinion, and apply the choices.
3. Finishing onboarding opens Discover. With a like, see shared-like evidence; with no usable likes, see explicitly labeled popular picks. Open a result to like/pass/save it and watch Discover update. Review Your Tasteprint to change or clear recorded opinions, and refresh to check persistence.
4. Open Ingredients, enter tomatoes, spinach, and chickpeas, then **Find recipes**. The pending input is included even if you have not pressed Add. Switch priorities to rerank. New-to-likes options appear first (12 initially, expandable); matching known favorites appear separately (six initially, expandable). Open any result for real details and normal like/pass/save actions. Passes exclude recipes; saves alone do not rank them. Editing/removing an ingredient clears obsolete results until you submit again.

Ingredient matching is a conservative name-rule layer, **not a newly trained semantic/learned hybrid**. It normalizes common plurals, preparation words and a few aliases; a small explicit family list handles names such as tomatoes/cherry tomatoes and chicken/chicken breasts. It does not substring-match egg to eggplant or milk to coconut milk, infer substitutions, or extract ingredients from arbitrary dish descriptions. Some legitimate matches will be missed. Every result matches at least one entered ingredient, but extra ingredients are allowed; expand a card to see original matched names and other listed ingredients. Distinct match counts prevent aliases/overlapping names from inflating coverage.

**A little of both** (default) sorts by ingredient coverage, then existing taste evidence, then other-ingredient count. **Ingredients first** sorts by coverage, fewer other entries, then taste. **Taste first** leads with taste among ingredient-matching recipes, then coverage and other-ingredient count. Within the new-options section, taste means raw average shared-liker scores when positive and training popularity otherwise; source ID breaks final ties. Known favorites are identified by explicit likes, not model guesses. No learned weighting or quality/diversity improvement is claimed. New-to-likes is not necessarily niche. No matches, loading and service failure are labeled without substituting fixed examples. See [Build 04 report](docs/BUILD_04_REPORT.md).

For the two optional API/decoder integration tests (Ingredients and MealMerge), keep Vite and the model running, then use PowerShell:

```powershell
$env:VITE_TASTEPRINT_LIVE_TEST = '1'
npm test
Remove-Item Env:VITE_TASTEPRINT_LIVE_TEST
```

Normal `npm test` skips those two live-server checks. Lifecycle/storage checks use a hook harness and presentation checks use static HTML rendering; neither is interactive browser verification.

### Try MealMerge

1. Open MealMerge. Your current Tasteprint is included automatically; Guest 1 starts with no invented opinions.
2. Choose **Edit guest choices**, name the guest and record actual likes/passes. Start with the 30 reviewed recipes, search ingredients/titles, or switch to all 5,006 model recipes. Guest browsing shows 12 cards at a time. Clicking the same opinion clears it; edits save as you go to the separate guest record. Add up to three guests, clear individual guest choices, or remove a guest and their record.
3. Choose **Find shared recipes**. Compare **Balanced compromise** (default) with **Overall appeal**, expand the evidence on a result, or use **Per-person evidence** for the comparison table. Results show 12 at a time with more available. Table/guest edits clear obsolete results and require another submission; changing priority or your own opinions reranks a submitted group. Result details affect your own normal likes/saves, not a guest's.

Both policies first favor recipes with evidence for more participants. Balanced then leads with the weakest supported relative position, average second; Overall leads with the average, weakest second. Explicit likes count as known evidence. Positive co-like scores become tie-aware positions within each person's own positive, unseen/unpassed recommendation pool so raw score scales do not dominate. Unknown entries are omitted from those aggregates, not converted to dislikes. A person with no usable choices remains visibly unknown; adding a blank guest does not shuffle the order. Any member's pass excludes that recipe only. Popularity breaks final ties and supplies a labeled fallback when all personal evidence is absent. Equal/weak profiles can produce identical mode orders.

These are hand-authored group-ranking policies, not a newly trained model, validated fairness outcome, satisfaction probability or dietary constraint. No ingredient matching is added to the group flow. Existing raw CF popularity concentration remains. See [Build 05 report](docs/BUILD_05_REPORT.md).

The model service now claims its port exclusively on Windows, so a second instance cannot falsely appear ready while an older service still handles traffic. Stop an existing service before starting another. `/api/health` identifies revision `build05`, lists supported features and retains its static `testScored: false` field. That field and the immutable ML 01–04 receipts describe the original serving/training stage, **not current project-wide test status**; ML 05 records the completed final evaluation separately. No serving code was changed for ML 05.

Open a recipe to see source directions, reported time/servings, listed ingredients, and Food.com/dataset links. Ingredient quantities are deliberately not invented. See [Build 02 report](docs/BUILD_02_REPORT.md) for catalog selection and verification. To reproduce the catalog from the downloaded audit inputs, install `requirements-data.txt` in `.venv`, then run `scripts/export_catalog.py` with that environment's Python. This is a deterministic export of `data/catalog-selection.json`, not model training.

Discover initially shows 24 cards with Show 24 more. Search filters the full model catalog while preserving rank. Saved can include already-liked/passed recipes. Fresh/Comfort labels apply only to the original reviewed collection. Serving supports one or more likes and popularity fallback for empty/all-pass/no-evidence profiles; measured ML quality used **six likes**, not every profile size. Source-record coverage is not recommendation diversity: raw CF's validation top tens used just 51 unique recipes. See [Build 03 report](docs/BUILD_03_REPORT.md) for verification limits and the larger bundle trade-off.

Saving is not liking. “Not for me” is a preference, not a dietary restriction. Closing onboarding without finishing discards its draft edits.

## Project guidance

- [Project brief](docs/PROJECT_BRIEF.md): product intent, candidate experiences, ML direction, and open technical choices.
- [Design standards](docs/design/DESIGN_STANDARDS.md): confirmed intent, reference analysis, and proposed design rules.
- [Design decisions](docs/design/DECISIONS.md): the design interview and the status of each choice.
- [Agent guidance](AGENTS.md): where to read before working on the project.
- [Collaboration standard](docs/COLLABORATION.md): explain completed work, discuss the next scope, agree, then implement.
- [Build plan](docs/BUILD_PLAN.md): milestones, ML explanations, and what the user needs to do.
- [Recipe-data research](docs/research/RECIPE_DATA_SOURCES.md): candidate sources, ratings, photos, access, and unresolved usage terms.
- [Local data audit](docs/DATA_AUDIT_01.md): measured Food.com results, practical limitations, and reproduction steps.
- [ML 01 protocol](docs/ML_01_PROTOCOL.md): source representation, six-choice ranking, user-disjoint split, metrics, and local commands.
- [ML 01 result](docs/ML_01_REPORT.md): measured comparison, limitations, and proposed next collaborative/hybrid discussion.
- [ML 02 diagnosis](docs/ML_02_REPORT.md): bounded content comparisons, missing-label/candidate coverage findings, and what remains unresolved.
- [ML 03 collaborative experiment](docs/ML_03_REPORT.md): first original trained model, new-user inference, simple hybrid results, verification and next discussion.
- [ML 04 approach comparison](docs/ML_04_REPORT.md): direct co-like models, bounded ALS tuning, profile controls and a provisional behavioral foundation.
- [Final held-out evidence](docs/ML_05_REPORT.md): frozen co-like versus popularity, uncertainty, discovery limits and immutable receipts.
- [Demo guide](docs/DEMO_GUIDE.md): preflight, short presentation sequence and recovery without clearing choices.
- [Demo readiness](docs/DEMO_01_REPORT.md): browser/runtime checks, test evidence and unresolved transient timeout.
- [Third-party notices](THIRD_PARTY_NOTICES.md): React Bits attribution and provisional photo provenance.

The accepted visual direction is implemented; smaller UI decisions and image sourcing remain iterative.
#   t a s t e - p r i n t  
 