# Tasteprint: October 4 demo guide

Prepared October 3, 2026. Local temporary demo, not a public launch. This is an adjustable three-to-four-minute rehearsal proposal; the exact presentation length and October 4 submission time have not been supplied. Confirm those with the organizer. [Readiness checks](DEMO_01_REPORT.md) and [ML speaking guide](EXPO_ML_EVIDENCE.md).

## Start on this laptop

Use this existing workspace and its existing Node dependencies, `.venv`, raw/model artifacts and source exports. Do not install, download datasets or retrain just before presenting.

In PowerShell:

```powershell
Set-Location 'C:\Users\imwri\OneDrive\Desktop\recipeapp'
npm run dev:all
```

Wait for both **VITE ready** and **Tasteprint local model ready: 5006 recipes**. Keep that terminal open. In another terminal in the same folder:

```powershell
.\.venv\Scripts\python.exe scripts/check_demo.py
```

Expect six PASS lines and `6 checks passed`. It checks the app HTML, model through the proxy, Discover, ingredient matches, shared group options and bulk directions. It submits a fixed QA fixture, not your preferences, and does not persist any choices or guests. It is an availability/contract check, not another model-quality evaluation or a browser test. A failed check exits nonzero; resolve it before presenting.

Open [your normal app](http://127.0.0.1:5173/#discover). Use this exact origin/browser for your existing profile. `localhost`, another port and another browser each have separate saved choices. Don't clear site data to make the demo work. Keep internet available for remote photos; the model runs locally. Some source records have no photo, and their fallback is intentional.

If you prefer the built production preview, keep the model running separately, run `npm run build` then `npm run preview`, and use port **4173**, not an arbitrary replacement port. Run:

```powershell
.\.venv\Scripts\python.exe scripts/check_demo.py --base-url http://127.0.0.1:4173
```

That is a separate profile from your usual 5173 origin. Switching ports is not a way to restore or copy saved preferences. The QA browser used `http://localhost:4173`, initially empty; its synthetic choices and `QA Guest` are not your personal demo profile.

## Before you show anyone

- Run preflight once after both services are ready; give it a successful run before starting the story.
- Open one bulk recipe and check directions and attribution. Open Ingredients and check that a short list returns real options. Return to the starting screen.
- Check Your Tasteprint shows your actual choices and saves. Do not replace them with the QA fixture or clear them for a cleaner-looking result.
- If including MealMerge, have a guest give real opinions in advance or identify staged example opinions explicitly. Keep their name/choices in the guest editor, not your own recipe dialog.
- Close unrelated heavy tasks and do a rehearsal on the presenting laptop. This is practical precaution, not an established explanation of the initial live-test timeout.
- Keep [the final ML results](ML_05_REPORT.md) available for questions. Do not rerun the final test or tune the model.

## A short sequence to rehearse

| Approximate time | Show | Explain |
| --- | --- | --- |
| 0:00–0:25 | Discover, or a brief landing-page introduction | “Tasteprint helps someone find real recipes from their own food preferences.” |
| 0:25–1:00 | Your actual preferences; optionally Refine your taste, then Discover | “Likes shape the order. A pass excludes that recipe, not its ingredients. Saving is different from liking.” With an existing profile, don't redo onboarding unless useful. |
| 1:00–1:30 | Your Tasteprint: select one note and its recipe evidence | “These visible notes are recipe-based estimates from what I liked, not the hidden model, measured flavour intensity or a liking percentage.” Bulk recipes remain unassessed. |
| 1:30–2:20 | Ingredients: enter `tomatoes, spinach, chickpeas`, Find recipes, expand a match | “This recipe matches these source ingredient names; these are the additional ingredients. I can emphasize ingredients or existing preference evidence.” Your results may differ with actual likes/passes. A priority change need not always change the first recipe. |
| 2:20–3:00 | Optional MealMerge: one guest, Find shared recipes, Per-person evidence | “Guest choices stay separate. We show the evidence for each person and leave unknown taste unknown.” Use the existing default; the deeper compromise trade-off review is deferred. Do not claim measured group satisfaction. |
| 3:00–3:40 | Explain the final comparison, without changing the app | “On 300 held-out historical people, six earlier likes led to a recovered later like for 107 people, versus 84 for popularity. Ranking improved too. It remains strongly popularity-heavy, so niche discovery is unfinished.” |

The default ingredient mode prioritizes coverage and then taste, not a trained blend. Do not promise a particular dish or three-of-three matches for every user's profile. Choose a visible result with understandable evidence, not a historical test success chosen to inflate the story. If time is short, omit the optional group section rather than rushing its limitations.

## Recovery without losing choices

| What you see | What to do |
| --- | --- |
| Recommendations unavailable / catalog order | Check the model terminal. Start `npm run dev:model` **only if no model is already running**, then use **retry recommendations**. Catalog browsing is not personalized while it is unavailable. |
| Ingredients or MealMerge couldn't load results | Restore the same model, then **Try again**. No sample results are substituted. Ingredient lists last only while the page stays open; re-enter them after navigation or refresh. Guest profiles persist separately. |
| Bulk directions unavailable | Restore the model and use the direction **retry**, or consult the original recipe link. The original 30 reviewed recipes have bundled directions; bulk steps need the local service. |
| Photo unavailable | Keep using the real metadata/directions or choose another recipe. Don't claim the picture is cached or replace it with an unrelated one. |
| Blank dev page / `504 Outdated Optimize Dep` | Stop only your Vite terminal, restart `npm run dev -- --force`, then reload. Keep the separately running model; don't clear browser storage or delete datasets. |
| Port already occupied | Find the existing Tasteprint terminal and use it or stop it with Ctrl+C. Don't run a second model or kill arbitrary Python/Node processes. A port conflict is not a reason to retrain. |
| Another timeout after otherwise healthy startup | Run preflight again and record the failing endpoint/message and which terminal was running. Stop the demo and investigate if it keeps failing; the earlier transient timeout's sole cause is not established. |

Use Ctrl+C in the terminal that started the launcher to stop its children when finished. If using separate terminals, stop each of your app/model/preview terminals. No account, API key, hosting or final-test rerun is needed.

## Your next step

Rehearse once with your real profile and guest opinions if applicable. Tell us the awkward transition or confusing explanation; agree on any final small polish before implementing it. This guide does not authorize new features or reopening the algorithm search.
