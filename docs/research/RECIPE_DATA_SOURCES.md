# Recipe-data sources for Tasteprint

Researched September 30, 2026. Deadline: October 4, 2026. Status: **research and proposals only**; no dataset was selected, bulk-downloaded, imported into Tasteprint, or used to train a model in this research milestone.

Follow-up: the user subsequently confirmed a local temporary demo and approved a practical audit, completed September 30. The larger Food.com version 2 files are now downloaded locally; see [measured audit](../DATA_AUDIT_01.md). The proposals and unmeasured statements below describe the earlier research milestone, not the latest implementation status.

## What Tasteprint needs

We need two different things: a trustworthy recipe catalog for Discover, and repeated preferences from identifiable users for learning historical taste patterns. A recipe's average rating is not enough to learn that different people prefer different meals. Photography also needs to depict the actual recipe, with its own provenance and usage terms.

This investigation inspected primary websites, author repositories/papers, uploader data cards, and one small official API response. All dataset totals below are **source-reported**, not row counts measured from downloaded files. Reported availability is not proof that downloads currently complete or that rights are cleared.

## Food.com: two distinct releases

### Authors-backed Recipes and Interactions

The research authors' repository links to Shuyang Li's Kaggle release. Their paper distinguishes a raw collection of over 230,000 recipes and one million reviews from the filtered research corpus of over 180,000 recipes and 700,000 reviews. These are source-reported totals, not local row counts. [Authors' repository](https://github.com/majumderb/recipe-personalization), [paper, section 4](https://aclanthology.org/D19-1613.pdf).

The live Kaggle card's License section, inspected in the browser on September 30, reads **“Data files © Original Authors.”** Do not describe this release as CC0 or assume unrestricted redistribution. The card is the data source; licenses on analysis notebooks or unrelated GitHub projects do not license its contents. [Uploader's dataset card](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions).

The live explorer's complete 12-field selection lists `name`, `id`, `minutes`, `contributor_id`, `submitted`, `tags`, `nutrition`, `n_steps`, `steps`, `description`, `ingredients`, and `n_ingredients`. There is no image field in that raw recipe schema. Its five review columns are `user_id`, `recipe_id`, `date`, `rating`, and `review`. Join candidates are recipe `id` and review `recipe_id`; recipe `contributor_id` means submitter, not the reviewing user. Version 2's explorer shows 892.41 MB across eight files, including raw tables and preprocessed artifacts. This verifies the advertised schema, not data quality or join coverage. [Live recipe/review explorer](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions).

**Tasteprint fit:** strong research provenance and a source of historical user preferences, but it does not solve photography for Discover. Rating meanings, joins, and permission scope need investigation before choosing a pipeline. It is not yet approved for use. Its original paper concerns personalized recipe generation; Tasteprint would use the data for ranking existing recipes, not adopt that generation model.

### Larger Recipes and Reviews release, including image links

Uploader `irkaal` reports 522,517 recipes, 1,401,982 reviews, and 271,907 users. Recipe content includes times, servings, ingredients, nutrition, and instructions; reviews include author, rating, and text. `Images` contains image URLs. The explorer reports approximately 68% empty image lists; that statistic is not our own measurement and remaining links may fail. The card recommends `recipes.parquet` and `reviews.parquet`; recipe CSV lists use R syntax. Its explorer reports a 1.55 GB package and its stated license is **CC0: Public Domain**. [Uploader's card and metadata](https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews/metadata).

The live `reviews.csv` explorer confirms eight fields: `ReviewId`, `RecipeId`, `AuthorId`, `AuthorName`, `Rating`, `Review`, `DateSubmitted`, and `DateModified`. This confirms that review rows include both user identity and a recipe reference. The recipe explorer exposes `RecipeId` and `Images`, so `RecipeId` is the candidate join key. Actual joins, repeated-user coverage, timestamp validity, and rating meanings remain unmeasured. Keep reviewer names out of the app and model features; IDs are for relating historical interactions, not identifying people to demo users. [Live recipe/review explorer](https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews).

**Tasteprint fit:** the most promising first audit candidate if we want one release containing both user histories and recipe-associated photos. Do not substitute recipe-author identity for reviewer identity. Existing image URLs need matching, availability, and permission checks; their presence is not confirmation of usable photos.

**Rights uncertainty:** an uploader's CC0 label is evidence of that uploader's stated terms, not confirmation that every Food.com contributor's recipe, review, or linked photograph is covered. Kaggle itself requires respecting others' content rights. We have not established an original-content/photo permission chain or public redistribution permission. [Kaggle terms, Content and User Submissions](https://www.kaggle.com/terms).

Food.com's footer reserves rights and links a Visitor Agreement. The linked agreement returned HTTP 403 to the research tool, so its contents were not reviewed. Public-demo/content reuse is an unresolved gate, not a permission conclusion based on that failure. [Original website footer](https://www.food.com/), [linked agreement](https://corporate.discovery.com/visitor-agreement/).

### Access and cleanup considerations

Kaggle staff announced unauthenticated public-dataset API downloads in 2024 while website downloads would still require login. Actual retrieval for these releases has not been tested here; do not tell the user an account or API token is definitely required before testing the supported public route. [Kaggle's public-download announcement](https://www.kaggle.com/product-announcements/485439).

For an approved audit, prefer typed Parquet when practical, keep original IDs, and parse list data as data rather than executing R/Python expressions. Source statistics and labels must remain separate from measured validation results.

## Other candidates

### Recipe1M / Recipe1M+

The authors report over one million recipes and 13 million images for Recipe1M+. Their schema describes titles, ingredients, instructions, and associated images, not a user-rating table. Unlike original recipe-linked photographs, the expansion uses title-based Google image searches and distributes photos among same-title recipes: an associated image is not necessarily a photo of that exact preparation. [Authors' paper, sections II-B and II-D](https://arxiv.org/html/1810.06553v2).

The official repository directs users to a request form for dataset access. That form could not be read with the research browser; turnaround, working download links, archive sizes, and dataset terms were not established. Its MIT software license is **not evidence of a dataset/photo license**. [Official repository](https://github.com/torralba-lab/im2recipe), [software license](https://github.com/torralba-lab/im2recipe/blob/master/LICENSE).

**Recommendation:** do not make this deadline's critical path depend on it. Its central strength is image/recipe representation research, not immediately available historical taste labels.

### TheMealDB

Its homepage currently reports 793 meals and 793 images. [Official homepage](https://www.themealdb.com/).

A small public lookup for recipe `52772` returned a recipe ID, category/area, instructions, ingredient/quantity slots, and a photo URL. It contained no user-rating history; its source, image-source, and Creative Commons confirmation fields were null. This is **one inspected payload**, not a database-wide quality audit. [Observed official lookup](https://www.themealdb.com/api/json/v1/1/lookup.php?i=52772).

The developer key `1` supports educational/development use. Documentation recommends a supporter key for public shipping, while the terms specifically prohibit free-tier app-store publishing. Confirm the appropriate plan for our actual public web demo rather than interpreting these as an unrestricted production grant. [API guide](https://themealdb.com/docs_api_guide.php), [terms](https://themealdb.com/terms_of_use.php).

The terms permit copying/modifying official API output, prohibit website scraping and removal of notices, require attribution for custom artwork, and reserve third-party-content rights. Check photo-specific metadata instead of calling every image CC-licensed. [Terms](https://themealdb.com/terms_of_use.php).

**Tasteprint fit:** simpler catalog fallback, but not a historical collaborative-filtering dataset. A recommender would need to learn from recipe content and our own collected preferences; this does not automatically provide an evaluated historical taste model.

## Proposed direction, not an implementation decision

First audit the larger Food.com Recipes and Reviews release because recipe metadata, user histories, and photo links could support both Discover and preference-model experiments. Keep the authors-backed release as a research reference/alternative rather than assuming the two releases have identical schemas, versions, or ID populations. Do not join them by recipe title.

With four calendar days until the stated deadline, favor an explainable content baseline plus one carefully evaluated learned model over image-model training or a multi-source merge. Data suitability, access, and usage terms are gates, not tasks to skip because time is short. If public display permissions remain unresolved, separate offline research from publicly displayed catalog content and agree on an alternative before shipping.

## Next bounded milestone for discussion

**Proposal: data access and audit, not model training or app replacement yet.** Once the user agrees on a candidate and the intended use:

1. Establish a supported download route and record version, original terms, provenance, file sizes, and hashes. Keep bulky raw files out of the public repository.
2. Measure actual recipe/review/user counts, unique IDs, missing fields, recipe-review join coverage, duplicate histories, rating distribution, and review dates. Confirm whether zero ratings are missing/unrated rather than dislikes.
3. Measure usable photo-link coverage without bulk image downloading. Inspect a small stratified recipe sample for content quality and exact photo correspondence, keeping rights unresolved unless evidence establishes them.
4. Check how many users have enough repeated ratings to support held-out evaluation. Outline a leakage-resistant split, then discuss which baseline and learned model to implement.
5. Bring findings back in Tasteprint terms: which real dishes Discover could show, what the model could learn from people's histories, what remains unsafe/unverified, and the next scope requiring agreement.

Deliverables would be a reproducible audit, a dataset/provenance manifest, and a proposed small demo catalog. No public data redistribution, Food.com scraping, purchased subscription, UI replacement, or training is implicitly authorized by this report.
