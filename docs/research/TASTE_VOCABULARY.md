# Tasteprint sensory vocabulary: bounded research

Researched October 1, 2026. Status: **research findings and app-specific proposal for discussion; no taxonomy, visualization, UI or model change approved or implemented.** Primary-source scan informed by `PROJECT_BRIEF.md`. The research skill's background-agent workflow supplied this note.

Subsequent decision, October 1: the user accepted the 18 definitions and approved UI 04's separate five-basic-taste wheel and broader constellation. The proposal and source scan below remain the research record. Implementation uses `src/data/sensory.ts` with explicit, metadata-estimated positive notes for the 30 reviewed recipes; it does not establish calibrated intensity or change model ranking. See `design/DECISIONS.md` D41–D43 and `UI_04_REPORT.md` for current status and verification.

## Established distinctions

The five commonly recognized basic tastes are **sweet, sour, salty, bitter and umami**. NIDCD describes umami as the taste associated with glutamate. Aroma, texture and chemical sensations also contribute to the overall experience of food. Chili burn and mint cooling belong to the common chemical sense (chemesthesis), rather than being additional basic tastes. Physical serving temperature is a separate attribute. The five tastes are a useful scientific foundation, but do not by themselves describe a whole meal. [NIDCD: How taste works](https://www.nidcd.nih.gov/health/taste-disorders).

A sensory lexicon supplies defined descriptors; a wheel can organize those descriptors. World Coffee Research's lexicon defines **110 coffee flavor, aroma and texture attributes**, with references for measuring intensity. It underpins the SCA Coffee Taster's Flavor Wheel. This is a strong example of shared language and calibration for a particular product, not a universal meal-preference model. [WCR Sensory Lexicon](https://worldcoffeeresearch.org/resources/sensory-lexicon), [SCA research store](https://sca.coffee/store/research).

UC Davis describes Ann Noble's **Wine Aroma Wheel** as a tool for standard terminology and learning to connect aromas to names. Its scope is wine aroma. [UC Davis on the Wine Aroma Wheel](https://www.ucdavis.edu/news/women-wine-and-chocolate-go-together-mondavi-institute-event).

**ISO 5492:2008** standardizes sensory-analysis terminology across industries: senses, sensory attributes and methods. **ISO 13299:2016** gives guidance for establishing sensory profiles, including relating perceived attributes to consumer acceptability. Their official public abstracts establish terminology and methodology; they do not supply a ready-made all-meal consumer preference wheel. Only the public summaries were reviewed, so this note does not claim full ISO compliance. [ISO 5492 abstract](https://www.iso.org/standard/38051.html), [ISO 13299 abstract](https://www.iso.org/standard/58042.html).

The SCA's current Coffee Value Assessment explicitly distinguishes **descriptive assessment** (sensory attributes) from **affective assessment** (personal or market-related impression of quality). This separation is useful for Tasteprint even though the coffee protocol itself is not a recipe protocol. [SCA Coffee Value Assessment](https://sca.coffee/value-assessment).

This bounded scan **did not establish a universally validated wheel that measures preferences across all meals**. That is a limit of the sources checked, not proof that none exists. A Tasteprint wheel or constellation should therefore be described as an app visualization of a controlled vocabulary and observed choices. Neither circular placement nor connecting nodes establishes scientific distances or a validated preference scale.

## Current local evidence

[describeTaste](C:/Users/imwri/OneDrive/Desktop/recipeapp/src/lib/taste.ts:62) counts tags on explicitly liked recipes and returns the four most frequent. It does not generate terms or measure sensory intensity. [catalog.ts](C:/Users/imwri/OneDrive/Desktop/recipeapp/src/data/catalog.ts:28) combines the 30 reviewed recipes with the bulk model catalog.

The 30 reviewed records contain 11 editorial tags: Brothy, Cheesy, Comforting, Creamy, Crisp, Fresh, Herby, Savory, Spiced, Tangy and Vegetable-forward. [export_catalog.py](C:/Users/imwri/OneDrive/Desktop/recipeapp/scripts/export_catalog.py:44) copies these explicit selection tags; [export_discover.py](C:/Users/imwri/OneDrive/Desktop/recipeapp/scripts/export_discover.py:36) puts each bulk recipe's source category into `tags`. The resulting profile mixes categories, sensory descriptors, ingredient/style descriptions and emotional associations. This is not a standardized sensory vocabulary.

In the reviewed [recipes.json](C:/Users/imwri/OneDrive/Desktop/recipeapp/src/data/recipes.json), 20 of 30 recipes have an ingredient name containing the word `salt` (simple name match, not a sodium or sensory analysis). Counting that ingredient would largely count exposure to a common ingredient. It would not establish preference for a notably salty dish or an ideal salt level.

## Proposed controlled vocabulary

**Proposal only:** 18 initial descriptors grouped by sense. These are practical app definitions, not an ISO list or a validated 18-dimensional preference instrument. A wheel and constellation can share this dictionary.

| Group | Canonical ID / display term | Working meaning |
| --- | --- | --- |
| Basic taste | `sweet` / Sweet | Perceived sweetness |
| Basic taste | `sour` / Sour | Tart or tangy taste; “Tangy” is an alias |
| Basic taste | `salty` / Salty | Perceived saltiness, not salt ingredient presence |
| Basic taste | `bitter` / Bitter | Perceived bitterness |
| Basic taste | `umami` / Umami | Glutamate-like savory taste; avoid treating all non-desserts as umami |
| Aroma | `herby` / Herby | Recognizable herb aromas |
| Aroma | `citrusy` / Citrusy | Citrus aroma; separate from sour taste |
| Aroma | `fruity` / Fruity | Fruit aromas other than the separately tracked citrus family |
| Aroma | `smoky` / Smoky | Smoke-like aroma |
| Aroma | `roasted` / Roasted | Toasted or roasted aromas; “Toasty” is an alias |
| Aroma | `nutty` / Nutty | Nut-like aroma; does not assert nut ingredients |
| Aroma | `warm_spiced` / Warm-spiced | Cinnamon/clove-like spice aromas; separate from chili burn |
| Texture | `creamy` / Creamy | Smooth, creamy mouthfeel |
| Texture | `crunchy` / Crunchy | Noticeable brittle/crunching bite; “Crisp” needs definition before merging |
| Texture | `chewy` / Chewy | Sustained resistance during chewing |
| Texture | `tender` / Tender | Easily yielding bite |
| Chemical sensation | `chili_hot` / Chili-hot | Chili-like burn/pungency, not serving temperature |
| Chemical sensation | `cooling` / Cooling | Mint-like chemical cooling, not cold serving temperature |

“Savory” could be an explained display alias for umami, but existing broad Savory tags require review before mapping. “Fresh” and “Spiced” are ambiguous and should not map automatically. Brothy and Cheesy can remain separately defined style/ingredient descriptors; Comforting is an association, and Vegetable-forward describes composition. Keep cuisines, ingredients and styles as separate facets instead of forcing them into sensory axes.

## Evidence and interpretation rules to discuss

Keep three questions distinct:

1. **Dish attribute:** Does this dish have a smoky aroma? Record the descriptor, provenance and whether it was directly assessed or estimated from metadata.
2. **Intensity:** How smoky is it? Use defined references if measured. A recipe label alone supplies no calibrated intensity.
3. **Preference:** Does this person like smoky food, and in what context or intensity range? Direct self-report is stronger evidence than a dish-level like for that specific claim.

Recipe titles, ingredient amounts and methods can support **estimated** descriptors. They are not a substitute for tasting: quantity, the whole ingredient mixture, cooking method and the prepared result matter. NIDCD explains that food releases molecules and aromas during eating and that concentration can change perceived intensity. Treat metadata-to-label rules as proposed heuristics requiring review, not measurements. [NIDCD taste explanation and concentration tests](https://www.nidcd.nih.gov/health/taste-disorders).

Liking one chili dish does not prove liking every chili level, every ingredient, or every tagged attribute. A safe snapshot says **“3 of your liked dishes are tagged smoky”**. That is an observed association; it is neither “smoky preference: 75%” nor intensity. A pass also does not identify which attribute caused rejection. Save actions remain separate from likes, as in the current product brief.

Use a finite dictionary with stable IDs, documented definitions, examples, labeling rules, explicit aliases and a version such as `sensory-v1`. Free text can be retained as source evidence but should not silently create new canonical categories. Distinguish **unknown/unassessed** from **assessed absent**; a missing metadata label supplies no evidence of absence, zero intensity or dislike. Confidence in an estimated dish label is separate from evidence about a person's preference. If a chart uses size, order, color or position, define exactly whether it represents count, evidence strength or directly reported preference. Final vocabulary and visual encoding remain decisions for user review.

Motion and React Bits Tilted Card remain design-discussion candidates after the vocabulary discussion; this note does not select a visualization or adopt a component. No recipes were newly annotated by this research.
