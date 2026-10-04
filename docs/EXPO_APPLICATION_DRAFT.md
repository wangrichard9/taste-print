# Tasteprint: IgniteAI Expo application drafts

Prepared October 1, 2026 at the user's request. These are submission-copy options, not approved new build scopes or a submitted application. Choose one track. Tasteprint remains the working project name.

## Recommended form answers

**Project title:** Tasteprint: Finding Food That Fits You

**Track:** Data Science

**Your "X":** Food, cooking, and everyday decision-making

**Project summary:**

Choosing what to eat should feel personal, but searching through recipes often means guessing what you will actually enjoy. Tasteprint is an in-development food discovery project that asks: can a few food choices help us find someone's next favorite dish?

I built a working web prototype where users explore real recipes, record likes and passes, save dishes, and see a visual summary of their choices. Alongside the app, I developed and tested recommendation methods using more than 300,000 historical recipe likes. I compared a pretrained AI text model, a model trained on rating patterns, and a method that learns which recipes people liked together. The latter uses someone's earlier likes to rank dishes they have not tried. I evaluated the methods on held-out users against a simple popularity baseline, rather than assuming a more complex model would work better.

My contribution is connecting an understandable food experience with evidence-based recommendation experiments. The longer-term vision includes ingredient-aware discovery and MealMerge: helping people with different tastes choose a meal together. Those features currently have sample previews; the tested recommender is not yet connected to the app.

## Alternative track summaries

Use the same title and X above. These are alternative framings of the same project, not additional entries.

### Artificial Intelligence

Tasteprint explores how AI can turn a few food preferences into suggestions for what to try next. I built a working recipe-discovery web prototype and developed recommendation experiments using more than 300,000 historical recipe likes. I compared pretrained text representations with a model trained on rating patterns and a recommender that learns which dishes people liked together. This last method ranks unseen recipes from a person's earlier likes. My contribution combines the food-choice experience with comparisons against popularity and held-out-user evaluation. The app already records choices, saves recipes, and displays a descriptive taste profile; the recommender is not yet connected to the app. Ingredient-aware discovery and MealMerge, a future shared-meal experience, currently have sample previews.

### Mobile & Web

Tasteprint makes exploring food more personal through an interactive web prototype. Users browse real recipes, search ingredients, record likes and passes, save dishes, and see their choices reflected in a visual Tasteprint. I built the interface, onboarding, recipe-detail views, and local preference storage, plus sample previews for ingredient-based discovery and shared meal choices. Alongside the app, I developed and compared AI recommendation methods using more than 300,000 historical recipe likes. My contribution connects a usable food-discovery experience with a tested recommendation workflow. The current app works for browsing and preference collection; the experimental recommender is not yet connected. The goal is to help people move from endless browsing to food that fits their tastes.

### Algorithms

Tasteprint investigates a practical ranking problem: given a few recipes someone likes, which unseen dishes should come next? I implemented and compared recipe-text matching, rating-trained collaborative filtering, and a method that scores dishes using patterns of recipes people liked together. The experiments use more than 300,000 historical likes and compare rankings against popularity on held-out users. My contribution is the implementation and controlled comparison of these approaches for food discovery, rather than a claim to have invented collaborative filtering. A working web prototype collects preferences and displays real recipes, while the recommender is not yet connected to the app. MealMerge is a future extension toward choosing meals for several people and currently exists as a sample interface.

### Software & Systems

Tasteprint combines a working food-discovery web prototype with a separate, reproducible recommendation pipeline. The app supports real-recipe browsing, search, onboarding, likes and passes, saved dishes, and a visual summary of recorded preferences. The Python experiments compare pretrained AI text representations and rating-based recommendation methods using more than 300,000 historical recipe likes. My contribution is connecting the product design, recipe-data preparation, local preference handling, and model evaluation into one project with clear boundaries between working features and sample previews. The next step is to connect the tested recommender to the app. Ingredient-aware discovery and MealMerge, a proposed shared-meal experience, are currently interactive previews rather than calculated recommendations.

### Business & Entrepreneurship

Tasteprint addresses an everyday frustration: having many recipe options but little help choosing food that suits you. I built a working web prototype where people explore real recipes, record preferences, save dishes, and view a visual summary of their taste choices. I also developed and compared AI recommendation methods using more than 300,000 historical recipe likes. My contribution is a product concept that links personal food choices to a measurable recommendation approach, with MealMerge as a proposed way to help households or friends choose meals together. This is an early product prototype: recommendation integration and user validation remain ahead, and group matching is currently a sample preview. Its intended value is less decision friction and more relevant food discovery.

## Track fit

The track descriptions below are paraphrased from the [official Expo site](https://igniteaiexpo.org/#tracks). Fit judgments are our assessment, not organizer eligibility decisions.

| Track | Fit for the present project |
| --- | --- |
| Data Science | Strongest overall: recipe data, preprocessing, held-out evaluation, and comparative experiments. |
| Artificial Intelligence | Strong: working ML experiments; describe the app/model separation clearly. |
| Mobile & Web | Strong: a working browser app; no native mobile-app claim. |
| Algorithms | Defensible secondary option: recommendation ranking and computational comparisons; no claim of a newly invented algorithm. |
| Software & Systems | Broad fallback: working app and separate data/model pipeline. |
| Business & Entrepreneurship | Possible product framing; stronger with actual user validation or a business case, which is not currently established. |
| Game & Animation | Weak for this build: interface motion supports the food app but is not its central project. |
| Cyber Security | Weak for this build: local preference storage is not a security project. |
| Robotics | No current fit: no robot or physical automation. |
| Hardware & Electronics | No current fit: no device or embedded system. |

## Website alignment and current status

The [Expo judging guidance](https://igniteaiexpo.org/#judging) prioritizes a working live demonstration, understanding the implementation, usefulness, and imagination. Its [rules](https://igniteaiexpo.org/#rules) require a project summary and participants' own extensions or improvements. AI tools are welcomed with disclosure and the ability to explain the work. These drafts communicate the problem, working artifact, method, contribution, and development status without portraying preview screens as functioning AI features.

The [official timeline](https://igniteaiexpo.org/#timeline) lists applications due **October 1, 2026, 11:59 PM Pacific** and Zoom interviews **October 4, 2026, 9:30–11:30 AM Pacific**. This distinguishes the application cutoff from the October 4 deadline recorded in the project brief. The rules limit each student to one entry per year; the supplied form has one track selector.

Current implementation evidence: [project brief](PROJECT_BRIEF.md), [ML 03 report](ML_03_REPORT.md), [ML 04 report](ML_04_REPORT.md), [real catalog report](BUILD_02_REPORT.md), [feature preview report](UI_03_REPORT.md), and the matching app source. The experiment uses 305,920 positive user-recipe pairs, 5,006 recipe candidates, and 300 validation profiles; the app catalog has 30 recipes. The reserved final test remains unscored. The visible taste profile summarizes explicit choices; it is not a learned taste embedding.

For judge questions, explain the pretrained encoder versus the rating models fitted for this project, the popularity comparison, and the current integration boundary. Disclose Codex/other AI development assistance and reused libraries accurately. Avoid describing the model as trained from scratch without qualification, reporting a ranking metric as enjoyment accuracy, or claiming ingredient matching, group optimization, or a validated hybrid model is already working.
