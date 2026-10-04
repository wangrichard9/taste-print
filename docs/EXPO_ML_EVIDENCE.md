# Tasteprint: explaining the recommendation evidence

October 2, 2026. Supporting measurements and caveats: [final report](ML_05_REPORT.md), [registered protocol](ML_05_PROTOCOL.md). This is a speaking guide, not a submitted presentation or a new app screen.

## A short explanation

Tasteprint starts with foods someone likes and recommends real recipes. Its current recommendation engine looks at patterns in historical recipe ratings: when people liked one recipe, which other recipes did those same people also like?

I compared several approaches rather than assuming a more complicated model would win. Pretrained text embeddings, latent-factor collaborative filtering and simple blends were explored on development data. For this dataset and evaluation, direct co-like relationships were the strongest selected behavioral approach, so that is what the app uses. It does not currently run a learned embedding/CF/XGBoost hybrid.

For the final check, I kept the model fixed and tested 300 different historical people not used to fit or select it. Each supplied six earlier likes. In ten recommendations, it recovered at least one recipe they liked later for 107 people, compared with 84 using popularity alone. It also placed recorded likes better overall. This is evidence that the personal choices help on this historical task—not a claim that the app knows every user's complete taste.

My main limitation is discovery: the recommendations still concentrate heavily on common recipes. Almost all top-ten slots come from the 100 most popular candidates. Many recommendations have no recorded rating from that person, so we cannot honestly call those suggestions good or bad from this dataset alone.

## What each part actually does

| Part | Honest description |
| --- | --- |
| Current preference engine | Tasteprint computes recipe-pair relationships from 305,920 historical positive user/recipe pairs, then averages the connections to someone's explicit likes. Scores are not enjoyment probabilities. |
| Discover | Reuses those relationships to rank unseen recipes; absent connections use labeled popularity fallback. |
| Ingredients | Conservative ingredient-name matching plus hand-authored priorities and the same preference evidence. Not another trained model or allergy filter. |
| MealMerge | The same preference evidence combined using explicit group rules. Individual evaluation does not validate group satisfaction or fairness; review is deferred. |
| Visible Tasteprint graphics | Summaries of explicit likes and metadata-estimated sensory annotations for the 30 reviewed recipes. Not the recommender's hidden vector or measured flavour intensity. |
| Earlier text model | Reused pretrained MiniLM embeddings, not fine-tuned or deployed as the current ranking engine. |
| Earlier latent-factor model | An ALS collaborative model trained by Tasteprint and compared during development, not the selected deployed method. |
| XGBoost / learned hybrid | Not implemented. Simple experimental content/CF blends were tested but not selected. |

## Numbers to explain carefully

- **107 versus 84 people:** at least one later recorded like in a top ten, out of the same 300 test people. This is 35.67% versus 28.00%, not a general accuracy percentage.
- **NDCG 0.07202 versus 0.05886:** a ranking measure that rewards a recorded liked recipe nearer the top. The paired improvement interval is positive: +0.00705 to +0.01924. It is not a match probability.
- **55 distinct recommended recipes:** across 3,000 co-like top-ten slots, out of 5,006 available candidates. The app can browse all 5,006; recommendations are not equally distributed across them.
- **99.6% of slots in the top 100:** the discovery limitation is measured, not dismissed.
- **94.1% unknown ratings:** these are recipes the person never rated in the observed future history, not proven dislikes.

The result applies to six-like, active historical reviewers inside a fixed catalog. It is not a global future forecast, a guarantee for an Expo visitor, a group benchmark or a dietary-safety claim.

## If someone asks what was learned

The most useful finding was that matching recipe descriptions was not enough for this particular held-out recommendation task. Historical behavior gave stronger evidence, but a more elaborate latent-factor model did not automatically improve it. The simple co-like approach earned its place through comparison and a final held-out check. It still has clear popularity and missing-label limitations.

## Proposed rehearsal, not an approved implementation

Show real choices changing Discover, use a short ingredient list to explain constraints plus taste, then optionally show MealMerge with clearly visible personal evidence. State the difference between measured individual-model results and hand-authored product rules. Choose real demo preferences with the user; do not pick historical examples solely because the final-test metric succeeds or invent visitor satisfaction labels. Agree on reliability/polish scope before making further changes.
