# Project brief

Source: the user's initial IgniteAI project brief and subsequent design request. Captured 2026-09-30.

## Product intent

Build a personalized food recommender for the IgniteAI Expo Data Science track. Tasteprint is a working name, not the final brand.

Learn meaningful food preferences from recipe data and user interactions. One underlying preference model should support multiple food experiences. The core recommendation system must work independently of an LLM.

## Candidate experiences

1. Personalized discovery: gather recipe preferences and recommend new dishes.
2. Ingredients to personalized recipes: retrieve real candidate recipes, then rank by preference, constraints, and ingredient availability.
3. MealMerge: recommend meals for several people, considering individual satisfaction and the fairness of the group outcome.

These are candidates for the MVP; their final priority and scope remain open. Pantry tracking, nutrition, meal planning, and recipe generation are later possibilities.

## Tasteprint and explanations

The internal representation may be learned and latent. The visible Tasteprint should translate supported patterns into understandable information such as ingredients, cuisines, flavors, styles, and avoided categories.

Explanations must reflect actual interaction history or model evidence. A displayed percentage must have a defined interpretation supported by evaluation; a ranking score is not automatically a probability of liking a meal.

## ML direction under consideration

**Current evidence, October 2:** the separately approved ML 05 final evaluation is complete. Frozen raw co-like ranking beats fitting-only popularity on the reserved 300-person/six-like/5,006-candidate task: NDCG@10 0.07202 versus 0.05886, with hits for 107 versus 84 people and a positive paired improvement interval. The fixed shuffled-seed contrast is also positive. It remains head-heavy: 55 distinct top-ten recipes and 99.6% of slots in the fitting top 100. No retraining, tuning, app change or new hybrid was added. Older paragraphs below describe original milestone stopping points, not current test status. See `ML_05_REPORT.md` and `EXPO_ML_EVIDENCE.md`; keep group, ingredient, sensory and visitor quality claims separate. MealMerge trade-off review is deferred at the user's request.

- Food.com Recipes and Reviews (`irkaal`, version 2) was downloaded and audited on September 30. Build 02 integrates 30 selected recipes into Discover; see `BUILD_02_REPORT.md`. ML 01 evaluates a pretrained semantic recommender against popularity outside the app; see `ML_01_REPORT.md`. It underperformed popularity on validation. ML 03 now trains collaborative factors and evaluates simple content/CF blends outside the app; see `ML_03_REPORT.md`. Further tuning, app integration and a potential XGBoost combining layer remain separate scopes to discuss.
- Content representations may use ingredients, tags, titles, descriptions, and pretrained recipe text embeddings.
- Collaborative filtering or matrix factorization may learn from historical ratings.
- A hybrid model may combine content and collaborative signals, potentially with a lightweight ranker.
- Start with simple baselines and compare experiments. Candidate metrics include Precision@K, Recall@K, NDCG@K, and task-appropriate classification metrics.
- ML 02's approved bounded content diagnosis is complete: text/profile changes give modest, uncertain gains, not a reliable solution. No simple embedding/index/truncation issue was found by the targeted checks. Incomplete observed ratings and limited candidates constrain interpretation; a need for more source data or a specific sole root cause has not been established. See `ML_02_REPORT.md`. No app method was replaced and final-test rankings remain uncomputed.
- ML 03's approved rating-trained experiment is complete: weighted implicit ALS fits 32-dimensional factors using 305,920 existing fitting-user likes. CF substantially improves over original text but still trails popularity; three simple blends trail CF. Correct-profile benefit over shuffled CF is inconclusive, and observed high/lower discrimination is near chance. Do not claim latent factors now capture nuanced human taste. No model was promoted into Discover, and final-test rankings remain uncomputed.
- ML 04's approved bounded comparison is complete. Direct raw co-like ranking is the provisional behavioral nominee (validation NDCG@10 0.06969 versus popularity 0.06205); direct normalized/shrunk ranking gives broader coverage but lower primary performance. Both show positive correct-versus-shuffled intervals, unlike all tested ALS variants. Raw recommendations remain highly popularity-concentrated and observed-rating AUC remains near chance. This is a selected validation finding, not an independently confirmed final approach or a launched recommender. Discuss freezing/final evaluation and app candidate/onboarding integration next; no further grid, XGBoost or text fine-tuning was added.
- Record dataset versions, preprocessing, training choices, evaluation splits, and the distinction between trained and reused components.

## New users

Explore a short onboarding experience with roughly 10–20 representative foods or recipes. Content signals may provide initial recommendations while further interactions improve the profile. Onboarding selection strategy and cold-start evaluation remain open.

## Competition priorities

Confirmed September 30: the intended Expo build is a **local, temporary personal demo**, shown to people but not hosted, launched, or publicly distributed. Keep source attribution and record the dataset's stated terms; do not assume attribution alone grants permission. Revisit publication requirements only if this scope changes.

Confirmed submission/demo deadline: **October 4, 2026**. The exact submission time and timezone have not been supplied. This is the next October 4 relative to the current project date, September 30, 2026.

Make the concept quickly understandable, the app polished, and the ML explainable. Deliver a strong, finishable MVP with a clear live demonstration. MealMerge is a candidate for the signature demo moment.

The user wants to understand and agree on each next implementation scope before work starts. See `COLLABORATION.md` for the authoritative discussion, approval, and handoff process.

**October 3 demo-readiness pass:** separately approved and complete. Existing flows, persistence, real source details and controlled model outage/recovery were checked in an isolated production-preview profile. Added a read-only local preflight command and `DEMO_GUIDE.md`, not another app feature or model change. All frozen final-evaluation receipts remain intact. See `DEMO_01_REPORT.md` for the actual checks and initial transient live-test timeout, whose sole cause remains unresolved. Rehearsal with the user's actual choices is the next user handoff; MealMerge trade-off review remains deferred.

## Technology

Build 01 uses React, TypeScript, Vite, custom token-based CSS, self-hosted Inter, Lucide icons, and Motion for the adapted React Bits Stepper. Preferences are local-only. This implements the user's request to begin building; it does not lock the backend or final data architecture.

UI 03 expands the Tasteprint profile and adds ingredient-entry and MealMerge group screens as explicitly approved design placeholders. Sample results and profiles are isolated fixtures; no recommendation or group engine is connected. Detailed layouts remain provisional for later user sessions.

Backend and ML: Python, FastAPI, pandas, NumPy, scikit-learn, and possibly SentenceTransformers, LightGBM, XGBoost, or a recommender library.

The project-local Python environment contains PyArrow/timezone data and the CPU-only embedding stack pinned in `requirements-ml.txt`. MiniLM weights are reused, not fine-tuned. Content experiments and original collaborative training/validation are complete; a learned combining ranker has not started. Builds 03–05 reuse the frozen raw co-like model through Python's standard-library loopback HTTP service, not FastAPI. The current frontend exposes all 5,006 model recipes, including the original 30 manually reviewed records. Historical model metrics are not validation of ingredient usability, safety or group compromise. See `BUILD_PLAN.md` for staged implementation.

**Build 03, separately approved October 1:** Discover now uses the saved raw co-like model through a loopback-only Python service. All 5,006 candidate recipes are browsable; 30 retain their manually reviewed editorial metadata and the other 4,976 use source metadata/directions without a manual-review claim. All original 30, including all six starters, are model-supported. Preferences/saves stay in the same browser storage; the local service receives recipe likes/passes without persisting them. Empty/no-evidence profiles fall back to labeled popularity; service failure is labeled non-personalized catalog browsing. One or more likes are supported mechanically, but benchmark quality was measured with six. No new training, hybrid/ranker, final-test scoring, Ingredients matching or MealMerge optimization is included. See `BUILD_03_REPORT.md` for verification and limitations; older milestone paragraphs describe their original stopping points.

**Build 04, separately approved October 1:** Ingredients now retrieves real recipes using conservative ingredient-name rules and orders them with the existing co-like model and ingredient coverage. Additional ingredients are allowed; new-to-likes options appear separately from eligible known favorites. Passed recipes are excluded and saves remain independent of taste. The three priority modes default to balanced. Source matches and other listed ingredients are visible without invented amounts or probabilities. These are hand-authored serving rules, not newly trained semantic embeddings, a learned hybrid ranker or evidence of nuanced/niche taste prediction. Ingredient lists are page-local; existing likes/passes/saves retain browser persistence. MealMerge remains a sample preview. Final-test scoring and retraining are not part of this milestone.

**Build 05, separately approved:** MealMerge now uses the current Tasteprint plus one to three editable local guest profiles. Guests are stored under a separate browser key and never become the person's own likes/saves. Both priorities favor recipes with evidence for more members; Balanced compromise defaults to maximizing the weakest supported relative position, whereas Overall appeal leads with the average supported position. Positive co-like positions are normalized within each person's own recommendation pool; explicit likes are known evidence, unknown entries remain missing, and recipes passed by any participant are excluded. Per-person positions/connections and popularity fallback are disclosed without satisfaction probabilities. This is hand-authored group aggregation, not another trained model or validated fairness/satisfaction outcome. No ingredients in group ranking, accounts, invitations, retraining or final-test scoring. See `BUILD_05_REPORT.md` for checks and review limits.

## Visual intent

The user wants a modern web app with an intentional, authored feel. Pinterest, Esquire, Buena, and Exactly.ai are direction references; Buena's typography and layout are especially appealing. Explore React Bits selectively for modern interactions. Detailed standards are developed in `design/DESIGN_STANDARDS.md`.
