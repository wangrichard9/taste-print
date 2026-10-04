# Build 02: real recipes in Discover

Completed September 30, 2026. User approved the real-catalog recommendation and explicitly deprioritized offline-demo support. No ML experiment, backend, redesign, or photo caching was included.

## What a person can do now

Browse 30 real Food.com recipes in the existing white/cobalt app, search their listed ingredients, use Fresh/Comfort/Saved filters, save dishes, and record explicit likes/passes. Open a recipe for source directions, reported time/servings, ingredient names, and original recipe/photo plus dataset links. Onboarding remains two rounds of three real starter recipes and a review, not a 30-item questionnaire.

Your Tasteprint counts editorial tags on liked recipes. Saves remain separate from likes. Discovery remains fixed editorial order, not personalized ranking. MealMerge is still a truthful planned-feature screen. No model was trained and no recommendation scores were invented.

## Data and presentation

- Source: [Food.com Recipes and Reviews](https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews), uploader irkaal, version 2. Raw-file provenance/hashes are recorded by the earlier audit.
- `data/catalog-selection.json` is the explicit 30-ID editorial selection and chosen photo indexes. `scripts/select_catalog_candidates.py` found candidates with nonblank ingredients/directions, aligned ingredient/quantity arrays, a photo, reported time at most 90 minutes, at least five reported reviews, and at most 20 instruction steps. These are display-candidate filters, not ML population rules or scientific relevance labels.
- Manual review inspected ingredient lists and all source steps for selected records. Candidates missing the main ingredient (pizza crust, noodles, chicken) were rejected, despite aligned arrays. The early sample/draft is not silently imported. A weak pesto-chicken photo/record was replaced with Mexican pasta salad after photo review.
- `scripts/export_catalog.py` validates recipe-file provenance/hash, preserves IDs, source titles, ingredient names and source instructions, and exports the explicit selection into `src/data/recipes.json`. Display names, descriptions, grouping and taste tags are editorial. HTML entities are decoded as text; no source HTML is injected.
- Thirty source-associated photos were visually reviewed in a local contact sheet, including alternate photos for weaker images. Six selected recipes use alternate image indexes. All 30 final images loaded with positive natural dimensions. This is a visual plausibility check, not independent verification of photographer identity, exact ingredients, or rights.
- Photos remain remotely linked to `img.sndimg.com`; they are not downloaded or packaged. The prior missing-photo fallback is retained. It was not independently forced in this milestone.
- No quantities/units are manufactured or paired into a measured shopping list. Even aligned metadata can omit ingredients or units. Details explicitly direct users to the original recipe before cooking and distinguish metadata from allergen safety. Source times may omit marinating/resting; they are reported values, not Tasteprint estimates.
- Actual reviewer names, review text, historical user IDs, and bulk raw files are not bundled into the app.

The original Food.com link format was checked on [Baked Salmon](https://www.food.com/recipe/baked-salmon-28199) and [The Ultimate Greek Salad](https://www.food.com/recipe/the-ultimate-greek-salad-90975). Other source URLs are derived from original titles and IDs and were not individually live-page checked. Source/dataset attribution appears inside the app and in `THIRD_PARTY_NOTICES.md`; no comprehensive permission determination is claimed.

## Local history

The real catalog uses `tasteprint:local:foodcom:v2`; Build 01 sample history remains untouched under `tasteprint:local:v1`. No sample like/save is reassigned to an unrelated recipe. Existing real-catalog choices survive onboarding edits and refreshes. A schema-version change was unnecessary: the new storage namespace separates catalog identity while retaining the existing validated preference structure.

## Verification

- `npm test`: **12 passing tests** across taste logic and catalog integrity. Covers unique source IDs/links, real-catalog storage separation, unknown/sample IDs, independent saves, opinion toggles, ingredient/filter search, editorial ordering, evidence counts, six starter choices, and time formatting.
- `npm run build`: passed TypeScript and Vite production build. Windows sandbox process-spawn restrictions required running verification with the approved escalation; no source workaround was introduced.
- Browser: Discover shows 30 recipes; `basil` search returns six; Saved combines with search; actual salmon directions/ingredients and attribution are visible; onboarding has three recipes per round and a correct starter-open count; Apply gives one like/one pass; refresh preserves profile and save; profile evidence reflects only the liked recipe; an unmatched query produces the empty-results state.
- Temporary verification likes, pass, and save were cleared via the UI without clearing browser storage. The onboarding-completed flag remains true in the test profile; it has no visible effect on the empty choice summary.
- Desktop and narrow-panel views were inspected. Requested 1280×800 and 1440×900 viewports produced document widths 1265 and 1425 respectively (scrollbar excluded), with no horizontal document overflow. Temporary viewport overrides were reset. Detailed phone optimization was not performed.
- Final selected photo contact sheet: 30/30 images loaded. Photo fallback retained but not forced; source page checks were limited to two pages, not all 30.
- `docs/build02-discover.png` captures the delivered Discover view. The local dev app remains available at `http://127.0.0.1:5173/#discover`.

## Reproduction

With the earlier dataset downloaded and `requirements-data.txt` installed in `.venv`:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/export_catalog.py
npm test
npm run build
```

Candidate discovery and photo-review helpers are optional audit tools; only the checked-in explicit selection determines the frontend catalog. The generated JSON is 52,545 bytes, not the full dataset. Final export SHA-256: `6f1fbac3db6e32e8b40347485220bc73633d29e3bfb3041e746a333f9a1d461f`.

## Next discussion, not implemented

Recommend agreeing on an explainable content-based recommendation baseline: compare recipe ingredients/styles with explicit likes, then evaluate held-out historical preferences against a non-personalized baseline. The broader audited data, not only these 30 display recipes, should inform a justified evaluation population. Discuss relevance labels, zero ratings, repeat-user requirements, test split, and cold-start behavior before implementation. Learned collaborative personalization and MealMerge remain later decisions.
