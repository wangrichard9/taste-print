# Tasteprint interview preparation

Prepared October 3, 2026 from the current project brief, serving code, ML 05 evidence and Demo 01 verification. These are spoken-answer drafts. Adjust personal inspiration, effort and time to your actual experience. They supersede the October 1 application draft's now-outdated integration and placeholder status; they do not alter that historical draft or approve further implementation.

## What is your project, and what does it do?

Tasteprint is a food recommendation web app. You choose recipes you like, and it uses patterns in historical recipe ratings to recommend other dishes. You can also find recipes using ingredients you have and use MealMerge to find shared options for people with different preferences. The app has 5,006 real recipes, with source ingredients and instructions.

## What problem does it solve, and why is it important?

Recipe search can tell you what exists, but it does not necessarily help you choose what fits your taste. Tasteprint combines your preferences with ingredient search and shared-meal choices, so you have more useful starting points for deciding what to cook.

This is intended value, not a measured reduction in decision time.

## What inspired you? Who benefits?

I wanted to explore whether a few food choices could become useful recommendations, rather than giving everyone the same popular recipes. The intended users are people looking for meal ideas and households or friends trying to choose food together.

Use a personal anecdote only if it actually happened; this wording describes the documented project intent.

## Can you walk us through how it works?

First, I record likes and passes through onboarding or recipe browsing. Those choices are stored in the browser. The frontend sends the recipe IDs to a local Python service, which loads the saved recommendation model.

The model contains connections between recipes, based on how many historical people liked both. It averages a candidate recipe's connections to my liked recipes, then ranks unseen recipes. Passed recipes are excluded; saves are stored separately and do not automatically count as likes. If there are no useful connections, the app labels its popularity fallback.

Ingredients first retrieves recipes with matching source ingredient names, then applies the selected ingredient/taste priority. MealMerge uses separate guest profiles and combines individual evidence under explicit group rules. The ingredients and group rules are programmed logic around the same recommender, not separately trained models.

## What AI component, programming languages and tools did you use?

The interface uses TypeScript, React and Vite, with CSS and Motion for presentation. The recommendation experiments and local service use Python. NumPy and SciPy handle numerical and sparse-matrix operations; pandas and PyArrow support data preparation. The recipe data comes from the Food.com Recipes and Reviews dataset.

I experimented with pretrained MiniLM text embeddings through SentenceTransformers, ALS matrix factorization trained on rating patterns, and direct item-to-item collaborative filtering. The current app uses the last approach, fitted from 305,920 historical positive user-recipe pairs. It is a statistical recommender, not an LLM that generates recipes. The Python service uses the standard library, not FastAPI.

## What was the most challenging part?

The biggest technical challenge was finding a recommendation method that actually improved on simply showing popular recipes. Text embeddings seemed promising, but they performed poorly on the task. The ALS model and simple blends also did not beat popularity in validation. Comparing the methods led to direct co-like relationships, which then performed better on the reserved final test.

Another challenge was separating missing evidence from negative evidence. If someone never rated a recipe, I cannot assume they disliked it. That affects how results are evaluated and how explanations are displayed.

This is a documented project challenge; choose which part was personally hardest for you.

## How did you test and debug it?

I checked both recommendation quality and software behavior. For quality, fitting users, validation users and final-test users were separate. After selecting the method, I froze it and evaluated 300 reserved users, each with six earlier likes, against recipes they rated positively later.

The top ten recovered at least one later liked recipe for 107 people, compared with 84 using popularity alone. This is a specific historical test result, not a general accuracy percentage. The final ranking score also improved. Recommendations still concentrated heavily on common recipes.

For software behavior, the latest readiness report records 100 passing Python checks, 68 passing frontend tests with live checks enabled, and a successful production build. Browser checks covered saved choices after refresh, recipe details, ingredient priorities, guest-profile separation, missing photos and a controlled model-service outage and recovery.

A live-test timeout was investigated using isolated reruns and direct versus proxied requests. It did not reproduce, so its exact cause remains unresolved. Do not claim every bug was fixed or that these checks were personally run without assistance.

## How long did it take?

The documented development sprint ran from September 30 through October 3, covering the app, recommendation experiments, integration and demo checks. It is a working local prototype with improvements still to make.

That is four calendar dates, not measured working hours. Add any earlier planning time only if accurate.

## Did you have assistance?

I used Codex for coding assistance, testing and debugging, along with existing libraries and a pretrained embedding model. My role included choosing the project direction, reviewing the behavior and deciding what to test and keep. I can explain how the parts work and which results support the current approach.

Do not answer a blanket “no”: AI assistance is part of the recorded development. Describe your actual role without claiming you manually wrote or independently understood every line. If asked about human assistance specifically, answer based on your actual experience.

## What did you learn?

I learned that a more complicated model is not automatically better. I also learned to compare against a simple baseline, keep final-test data separate from model selection, and explain what a score means. Making a model useful required connecting it to real choices, source recipe data and clear fallback behavior.

## What would you improve with more time?

I would work on less-popular recipe discovery, because the current recommendations still favor common dishes. I would evaluate more representative onboarding choices and collect feedback from real users. For MealMerge, I would test whether the compromise rules actually help people agree on a meal, rather than treating individual-model results as proof of group satisfaction.

These are potential improvements, not approved build scopes or promised outcomes.

## Technical follow-ups to rehearse

**How is the current model fitted?** A sparse matrix records which fitting people liked which recipes. Ratings of four or five stars count as positive. Multiplying its transpose by itself counts shared likers for each recipe pair. Self-connections are removed. The saved relationship matrix is loaded for serving; browsing does not retrain it.

**Can you give a scoring example?** As an invented arithmetic example, if a candidate has 12 shared likers with one liked recipe and eight with another, its average connection score is ten. That ranks connections; it does not mean a ten-percent chance of liking the dish.

**Why test embeddings if they are not used now?** They offered a way to compare recipe meaning, but comparison with popularity and behavioral methods did not support choosing them for the current ranking task.

**Is the visible Tasteprint the model's hidden representation?** No. The wheel and constellation summarize explicit likes using metadata-estimated sensory annotations for the 30 reviewed recipes. Bulk recipes remain unassessed. These graphics are not measured flavour intensity or predicted enjoyment.

**How does MealMerge choose?** Both modes first favor recipes with evidence for more group members. Balanced compromise then prioritizes the weakest supported relative ranking position; Overall appeal prioritizes the average. Unknown evidence stays missing, and any participant's pass excludes that recipe. These are explicit aggregation rules, not validated satisfaction probabilities.

**Does liking curry imply liking every curry ingredient?** No. Recipe likes create recipe-to-recipe evidence. A pass excludes that dish, not its ingredients or cuisine. Ingredient matching uses separate name rules and is not an allergy guarantee.

## Supporting evidence

- [Current project brief](PROJECT_BRIEF.md)
- [Plain-language ML evidence](EXPO_ML_EVIDENCE.md)
- [Final evaluation](ML_05_REPORT.md)
- [Readiness verification](DEMO_01_REPORT.md)
- [Live-demo guide](DEMO_GUIDE.md)
- [Recipe relationship implementation](../scripts/co_like.py)

No new tests or experiments were run for this writing task; verification claims above are attributed to the completed reports.
