# UI 03: feature screen placeholders

Implemented following the user's explicit request to build the remaining screens while another agent researches the recommendation process. Decisions D35–D37 record the UI-only scope and provisional design status.

## What works

**Your Tasteprint** now has a visual profile summary, explicit liked/passed/saved counts, tag-frequency bars, overview/choices/saved views, choice filters, and a saved-recipe collection. Existing local opinions and saves continue to drive the real profile. Its Build/Edit action opens the existing onboarding. Starting onboarding from the example view switches back to the real profile before collecting choices.

Explore an example provides a populated fixture with four likes, two passes, and three saves. The example has its own clear label and never writes those values into the real profile. Inspiration cards are fixed sample picks, not predictions.

**Ingredients** is a new app tab. Visitors can enter comma-separated ingredients with Enter, add suggested items, remove chips, clear the list, and choose an ingredient/taste/balanced priority. Input deduplicates without regard to case and caps the list at 12 ingredients and each item at 40 characters. Pending input is committed when opening sample recipes. Clearing or editing ingredients/priority hides the old sample result state.

Show sample recipes displays three fixed real-catalog recipe cards. The entered ingredient list and selected priority are echoed for reviewing the proposed interaction, but neither changes the recipes or their ordering. Ingredient similarity, missing ingredients, and taste ranking are unimplemented. Empty entry cannot open results.

**MealMerge** replaces the roadmap-only page with a sample table. Four authored sample people have visibly different taste tags. Visitors can add/remove them, preview a shortlist with at least two people, switch between meal ideas and individual comparison notes, and return to edit the table. The comparison's columns follow the selected sample people. On narrow screens it scrolls inside a focusable region, including with the keyboard.

The meal shortlist and each person's explanatory notes are authored fixtures. There is no group optimization, calculated satisfaction, profile sharing, invitation, account, or matchmaking service. No percentages are invented.

**Recipe details and navigation** work across all four app tabs. Sample-result and example-profile cards use read-only details with source ingredients, instructions, and attribution. Their dialogs have no Like/Pass or Save actions. Discover and the real profile keep the existing editable details and local persistence. Discover's MealMerge tile now leads into the sample flow.

## State and integration boundaries

`src/data/feature-previews.ts` owns authored examples and references real recipe IDs. The three page components handle temporary screen state; they do not call any model or ranking API. Ingredient lists, priorities, sample profile mode, and group selections reset when leaving their screen or refreshing. Only the existing real opinions and saves persist. The app's storage schema/key and Python/ML code are unchanged. Existing online recipe images retain their missing-image fallback.

`src/features.css` builds on the shared white/ink/cobalt tokens, Inter, restrained component geometry, and native controls. No dependency was added. Final layouts and detailed interactions remain open for later user sessions.

## Verification

- Production build and TypeScript passed; the existing frontend suite's 12 tests passed.
- Empty and populated example Tasteprints render. Choice filtering showed two sample passes; sample saved view showed three recipes. Returning to the real profile restored zero/zero/zero rather than copying sample data.
- Recipe details opened from sample profile and ingredient cards contained no opinion or save controls; Escape dismissed them. Starting onboarding from the example and canceling returned to the real profile without applying example data.
- Comma/Enter input deduplicated Tomatoes, Spinach, tomatoes to two chips. Removing a chip, adding a suggestion, selecting Taste first, opening three results, and clearing the list worked. A 41-character ingredient produced the intended validation message. Empty input disabled results.
- One selected group member disabled Preview shared picks. Adding Maya/Jordan produced three recipe ideas; comparison showed four columns (recipe plus three people) and three rows. Editing the table retained the three selections. Mobile ArrowRight moved the table scroll position by 40px without widening the document.
- Discover's real detail dialog retained its opinion/save controls after visiting sample flows. A temporary Greek salad like/save appeared as one like and one save in the expanded profile and survived refresh. Unsave and the repeated Like action restored the original empty profile; test choices were cleaned up.
- Checked 1440×900, 1280×800, 1024×800, 820×900, 390×844, and 320×760 across the new screens, including populated states. The document had no horizontal overflow. The comparison table's intentional overflow stayed inside its own region. Temporary viewport overrides were reset.
- Final browser console inspection returned no errors.

These reversible placeholder flows were verified in the real browser rather than adding unit tests that duplicate their CSS or static fixture strings. Existing preference/catalog tests remain the regression suite for the underlying working behavior.

## Previews and review

- [Tasteprint summary](design/previews/ui-03-tasteprint.jpg)
- [Ingredient flow and sample results](design/previews/ui-03-ingredients.jpg)
- [MealMerge sample shortlist](design/previews/ui-03-mealmerge.jpg)
- [Individual comparison](design/previews/ui-03-comparison.jpg)
- [Narrow comparison](design/previews/ui-03-mobile.jpg)

Try Your Tasteprint → Explore an example; Ingredients → Use example ingredients → Show sample recipes; MealMerge → select sample people → Preview shared picks → Taste comparison. Review the composition and flow before choosing detailed refinements or integrating the engine.
