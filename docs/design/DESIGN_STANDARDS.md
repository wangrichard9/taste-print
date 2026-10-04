# Design standards

Status: Build 01 implements the accepted foundation. Smaller details remain iterative. Confirmed direction is authoritative; implementation tokens are adjustable, not individually approved specifications.

## Confirmed intent

- Build a modern web app with an intentional visual identity and polished interactions.
- Use the references as direction, adapting them to a food recommendation product.
- Give special attention to Buena's typography and overall layout.
- Consider React Bits for selected UI elements.
- Establish the design through a back-and-forth interview with concrete options.
- Prioritize laptops for the first build and competition demo. Mobile optimization is a later concern.
- Use quiet editorial as the app's foundation, with some visual studio energy.
- Make the public landing page more expressive and distinctive while preserving a coherent identity with the app.
- Use selective motion: restrained everyday feedback plus occasional meaningful expressive moments.
- Favor bold, crisp color over warm, cozy palettes. Avoid glowing gradients, generic typography, and cheap or inconsistent imagery.

## Reference interpretation

Observed 2026-09-30. Websites can change; the interpretation is specific to the inspected pages.

| Reference | Observed or supplied signal | Proposed translation to Tasteprint |
| --- | --- | --- |
| [Buena](https://buena.com/en/home) | Large sans-serif headings, generous margins, simple image blocks. The inspected hero uses Inter Display medium, 56px text, 64px line height, and -1.12px tracking at its desktop viewport. | Clear hierarchy, deliberate line breaks, restrained weight, and room for food imagery. The sampled dimensions are reference measurements, not app tokens. |
| [Esquire](https://www.esquire.com/) | Strong masthead, thin dividers, varied column sizes, and a prominent lead image among denser supporting stories. | Editorial pacing, purposeful image hierarchy, and useful recipe metadata. |
| [Exactly.ai](https://exactly.ai/) | Immersive photography behind a large sans-serif headline and compact navigation. | A selective photographic brand moment or onboarding introduction. |
| [Pinterest](https://www.pinterest.com/) | User-supplied discovery reference. Inspected public pages show prominent search and compact navigation; Explore remained in a loading state. | Explore image-first food browsing. Masonry is a proposed interpretation to test, not a verified observation of the loaded feed. |

## Confirmed direction

### App: quiet editorial with visual studio energy

Use Buena-led sans-serif typography, deliberate spacing, clear hierarchy, and high-quality food imagery. Add visual studio energy through selected compositions, crisp cobalt accents, and purposeful interaction. Use restrained app typography, compact top navigation, and modest component rounding with crisper imagery. Exact font files, spacing tokens, and recipe presentation details remain open.

### Landing page: expressive extension

Use larger and bolder display type, more distinctive composition, and a small number of expressive moments on the landing page. Share the app's font family, white-and-cobalt identity, and basic control language so entering the product feels continuous.

Lead the story with finding food and enjoyment. Show understanding the person's taste as the underlying idea that makes Tasteprint distinctive. Balance the hero's headline and readable product/profile preview with supporting food imagery; food photographs must not dominate the composition.

Use the user's Airvoir reference for a concise immediate-action area and gradual scroll storytelling. Include both a three-food trial and an animated app demonstration; their placement and detailed behavior remain open. Motion should connect food choices to understandable taste patterns. Keep scrolling under the visitor's control and keep essential information readable. Detailed scroll chapters remain open pending discussion.

Build enough composition around readable product previews and supporting imagery to convey character and substance. An entry-flow comparison is not the final landing composition. Avoid using empty space or decorative taste diagrams as substitutes for showing the app's experience.

Give the landing hero a recognizable visual anchor: one signature graphic or composed product element that establishes Tasteprint's character even at thumbnail size. Use the user's supplied landing-page gallery to study this role. The accepted form is option A: a composed product scene with readable food-choice and Tasteprint panels. Supporting food photography introduces the choices while the profile and typography carry most of the visual weight. Connect the demonstration and real food trial through this shared composition. Detailed choreography remains iterative. Profile patterns must reflect explicit choices or be clearly marked as a demonstration.

The first landing milestone covers the landing page and reusable animation components. Expand motion throughout the app after reviewing this language. Start with the existing Motion engine, select React Bits components for specific roles, and add GSAP when a chosen sequence justifies it. Library suggestions do not require using every engine.

The user favors the reviewed Card Swap composition and especially Scroll Reveal's gradual text treatment. Do not adopt the reviewed draggable Stack or Scroll Stack treatments for this pass; the user dislikes their popping/stacked feel. Scroll Expand and curtain reveal were also declined for this pass. Implement a composed, layered hero with deliberate scene transitions and slow scroll-linked text reveal. Keep demonstration choices separate from saved preferences.

Use React Bits Star Border on a few landing buttons or icon controls. The user's explicit request permits this small border effect as an exception to the earlier decorative-glow exclusion; it does not authorize broad glowing surfaces or background gradients. Keep Ripple Distortion on the supporting food illustration with a static fallback. Remove the visible Still/Ripple comparison controls after the first review. Make the illustration itself keyboard-operable to trigger a ripple. Do not distort app controls.

The user explicitly removed reduced-motion suppression on the landing page. Play the slow story blur reveal, ripple interaction, Star Borders, text/section entrances, scene transitions, card hover/focus, and smooth Back to top normally regardless of the system flag, without a visible motion toggle. Preserve readable text, manual scene navigation, and the static illustration fallback for loading or unavailable WebGL. This landing-specific decision does not change the existing onboarding/app motion policy or operating-system settings.

The next landing pass is an approved scale experiment: increase meaningful content sizes, narrow laptop outer margins, and give major sections approximately a viewport of space so they arrive individually during free scrolling. Do not add scroll snapping or wheel interception. Keep the earlier proportions available through the base stylesheet; isolate larger sizing in a removable experiment stylesheet. Try restrained enlargement on food-card hover and keyboard focus, without overlap or layout shifts.

Refine the reviewed larger composition with a slightly wider closing cobalt banner and a modestly larger hero heading. The process heading must scroll normally rather than stick to the viewport. Watch the app must play its complete timed demonstration with the composed scene transitions. Stop, replay, and manual stage navigation must remain available.

### Color and imagery

Use a white primary canvas with dark text and cobalt accents. Dark ink is a text color, not the default app background. Use cobalt for primary actions, active navigation, selected states, and occasional intentional brand elements. Keep large surfaces white, with pale cool neutrals for secondary surfaces and thin dividers. Initial reference values: white `#FFFFFF`, ink `#17191E`, cobalt `#2647EB`; exact tokens may be tuned after screen review.

Warm cream, beige, terracotta, and a cozy food-magazine treatment are outside the selected direction. Glowing decorative gradients are excluded by the user's explicit preference; use solid color and photography to create character.

Curate imagery for consistent quality and art direction. Food photography can naturally contain warm colors; the rejected warmth concerns the interface palette and overall treatment.

Build 02 uses recipe-associated Food.com photography loaded online; offline caching is explicitly not a current priority. Retain graceful missing-image behavior. Display source attribution and keep original recipe identity separate from editorial display names, summaries, and taste tags. Ingredient metadata is not a complete measured shopping list or dietary-safety guarantee. Preserve source instructions, label reported times, and link to the original recipe rather than inventing missing amounts or units.

Build 03 expands Discover to all 5,006 model recipes while preserving the 30 reviewed records. Label bulk imports as source metadata, not manual review. Render cards in bounded batches; fetch bulk source directions on demand. Show shared-liker evidence only when supported, label popularity fallback explicitly, and never disguise loading or service failure as personalized ranking. Already liked/passed dishes stay out of Discover recommendations but remain accessible through recorded choices/saves. Fresh/Comfort labels on the reviewed collection are editorial, not model classifications. Landing product scenes and profile sample picks remain labeled illustrations; current MealMerge behavior is governed by Build 05 below.

Discover keeps automatic like/pass updates and also exposes a native secondary Refresh recommendations button above the filters (D48). Disable it during requests, show Refreshing feedback, and confirm the completion time only after the latest response is validated. Preserve search/filter choices and saved preferences; refresh reranks rather than retrains, and the order can remain similar. Never label a previous request's result as the refreshed one or imply success when the service is unavailable.

Build 04 connects Ingredients to real matches from the same model catalog. Preserve the editorial white/cobalt layout. Every result must match at least one entered ingredient name using conservative, disclosed rules, with no substitution or safety claim. Allow additional ingredients; report matched source names and other listed ingredients separately. Count distinct matches without double-counting aliases or overlapping names. Balanced (default) prioritizes coverage then taste; Ingredients first prioritizes coverage then fewer additional entries then taste; Taste first prioritizes taste among ingredient matches. Taste means explicit favorites/shared-like evidence, with clearly labeled popularity fallback when unavailable—not descriptive profile tags. Show new-to-likes recipes first in their own bounded, expandable section and matching known favorites separately. Do not equate new with niche or claim the model is more diverse. Exclude passed recipes, keep saves independent of ranking, and open real source details with normal choice/save actions. Ingredient edits clear obsolete results; priority or explicit opinion changes rerank the submitted list. Label loading, service failure, retry and no matches truthfully; never silently replace them with fixtures. The ingredient list is page-local, not a persisted pantry or measured shopping list.

Build 05 connects MealMerge to the existing model without changing visual direction. Show the current person and up to three editable local guests, with real recipe-choice controls, bounded searchable guest browsing, clearly separate storage and honest empty/weak-profile states. Default to Balanced compromise, offer Overall appeal for comparison, and disclose that broader member evidence precedes either supported-position policy. Unknown evidence stays unknown rather than becoming a low satisfaction score. Show explicit likes, actual shared-like positions/connections, partial evidence and labeled popularity fallback per recipe/person; do not manufacture group match percentages. A recipe passed by any member is omitted, not treated as an ingredient/allergy ban. Real result details affect only the current person's normal likes/saves; guest opinions are edited in their own clearly named editor. Keep loading/error/retry and obsolete-response handling honest. Guest/table edits require a new group submission; priority/current-person opinion changes rerank a submitted group. Do not use sample people, fixed group recipes or authored preference notes as live output. Landing/profile sample scenes remain illustrative. Guest records are browser-local, not shared accounts.

### Typography and component geometry

Use one shared sans-serif family initially. App headings should be restrained and deliberate; the landing page can use larger and bolder display treatments. The prototype may use Inter as a Buena-aligned reference, while exact font files remain open.

Use modest, consistent rounding on controls and dialogs, and crisper image containers. Build 01 uses 8px controls, 2px images, 6px brand panels, and 12px dialogs. Inter Variable is self-hosted. Treat these as implementation starting points for review, not separately approved specifications.

### Navigation and first design test

Use compact top navigation for Discover, Your Tasteprint, and MealMerge. Discovery is the first full-screen design test. Validate the visual language with recipe content before extending it to other screens.

The approved feature placeholder pass adds Ingredients to the compact app navigation and expands Your Tasteprint and MealMerge using the existing editorial type, cobalt, image crops, and native control language. Provide usable overview/choices/saved views, editable ingredient chips and priority controls, and group setup/comparison states. Treat the layouts as provisional for later user testing. Fixed ingredient/group result fixtures and example profiles must be visibly identified as samples; do not present them as personalized outputs or fabricate match percentages. Keep fixture state separate from real saved choices and use read-only recipe details for sample flows. No extra animation library or engine integration is part of this pass.

UI 05 adds a compact floating app navbar inspired by AccessGrid, with a travelling active/hover highlight and lightweight illustrated destination previews for Discover, Your Tasteprint, Ingredients and MealMerge. Keep direct links and an ordinary keyboard order. Hover/focus explores a destination; clicking navigates immediately. Dismiss previews on Escape, pointer/focus departure or navigation, and keep touch/narrow navigation usable without previews. Destination graphics are conceptual decoration, not personal evidence. Share restrained spring/arrival timing with gliding Tasteprint view indicators, short view-content transitions and responsive existing navigation tiles. Preserve all recipe, preference, request, guest and saved state behavior; recipe-card expansion is deferred. Per explicit user decision D47, always animate this navigation package even when the device requests reduced motion; use a narrowly scoped Motion override and do not add settings. The separate diagram/onboarding policy remains in place.

### Laptop priority

Design the main experience around laptop viewing, keyboard and pointer use, and the first competition demo. Plan initial checks around 1280×800 and 1440×900 viewports. These are proposed verification sizes, not final layout breakpoints. Keep basic reflow without making phone-specific navigation or interactions a first-build priority.

## Proposed quality rules

- Set a consistent type scale, spacing scale, color vocabulary, and component states before extending the UI.
- Let hierarchy come from type, alignment, spacing, and photography. Use containers where they define a meaningful grouping or interaction.
- Choose image crops and aspect ratios deliberately. Preserve the relationship between a recipe and its actual image, and design a fallback for missing images.
- Use specific food language and evidence-based explanations of recommendations.
- Design loading, empty, error, selected, disabled, and focus states alongside the successful state.
- Support keyboard interaction, readable contrast, touch targets, and reduced motion.
- Validate layouts with real content, long recipe names, missing images, and different laptop widths. Keep narrower windows usable through basic reflow.
- Keep displayed recommendation evidence and uncertainty consistent with the model's actual output.

### Your Tasteprint: sensory wheel and constellation

UI 04 adopts the researched 18-term controlled vocabulary with stable IDs, definitions and aliases, separating basic tastes, aromas, textures and chemical sensations. Show a dedicated wheel for Sweet, Sour, Salty, Bitter and Umami and a separate constellation for the broader vocabulary. Keep the white/cobalt editorial identity; make words and recipe evidence prominent and reduce the visual dominance of counters.

Wheel petal radius represents the number of liked recipes with that sensory note, on a common liked-recipe count scale. Notes are authored estimates from the original 30 reviewed recipes' metadata, not calibrated sensory measurements. A missing descriptor means unassessed, not absent, disliked or zero intensity. Display annotation coverage and expose the recipe-specific basis on selection. Never treat bulk category tags as sensory attributes or automatically map broad Savory/Spiced/Fresh labels into the dictionary. Constellation geometry is compositional, not a learned similarity map.

Use native keyboard-operable controls for petals/words, readable definitions, honest empty/sparse states, and isolated example choices. Use the existing Motion engine for selective entrances, line drawing, selection and evidence transitions. Adapt React Bits Tilted Card only for supporting recipe images with restrained rotation/scale, a keyboard focus equivalent and static touch/reduced-motion behavior. The landing-specific motion override does not extend to the app. These graphics explain choices and do not alter recommendation ranking or saved data.

## Motion and React Bits candidates

Tasteprint diagrams support transient hover/focus exploration separately from committed selection. Lift wheel sectors by a few pixels while preserving their data radius; include full-sector pointer targets even for sparse petals. Show the explored word's definition within its panel. Constellation exploration highlights the matching connection, with a brief travelling dot and central ripple. Clicking commits recipe evidence; hovering must not change preferences or constantly replace that evidence. Use the same previews for keyboard focus, retain touch selection, and avoid continuous ambient loops. Honor app system motion preferences without adding visible settings.

Build 01 adopts React Bits' TypeScript Stepper source for onboarding, adapted in `src/components/react-bits/Stepper.tsx`. It uses native step buttons, backward-only indicator navigation, final-step validation, resize-aware content, and reduced-motion support. Landing 01 also adapts Scroll Reveal, Star Border, and the optional Ripple Distortion experiment. The layered hero uses custom Motion code. Everyday feedback uses 160–220ms transitions; onboarding transitions travel 16px. These timings remain tunable. Other candidates below are proposals. React Bits is a source of adaptable components, not the entire design system.

| Candidate | Possible use | Adoption consideration |
| --- | --- | --- |
| [Stepper](https://reactbits.dev/components/stepper) | Preference onboarding | Adapt its styling and step semantics; verify keyboard controls. |
| [Animated Content](https://reactbits.dev/animations/animated-content) | A selective content entrance | The source uses GSAP; evaluate whether the existing animation engine or CSS is sufficient. |
| [Counter](https://reactbits.dev/components/counter) | One meaningful result changing | Provide stable accessible text. Use only numbers whose meaning is supported. |
| [Masonry](https://reactbits.dev/components/masonry) | Browsing recipe images | Test bounded image loading, reading order, and responsive layout. Use aligned layouts when comparing options. |
| [Stack](https://reactbits.dev/components/stack) | A possible recipe choice interaction | Dragging must have explicit, accessible alternatives; the stock stack is not a preference model. |
| [Blur Text](https://reactbits.dev/text-animations/blur-text) | An optional profile heading reveal | Keep essential text readable and honor reduced motion. |

Use motion to explain a selection, a transition, or a result. A MealMerge animation should represent real group information rather than imply unsupported relationships.

The inspected [React Bits license](https://github.com/DavidHDev/react-bits/blob/main/LICENSE.md) is MIT plus Commons Clause. Its notice is preserved alongside the adopted Stepper; provenance and changes are described in `THIRD_PARTY_NOTICES.md`.

## Still to resolve

See `DECISIONS.md` for the current status. The palette direction, typography treatment, component geometry direction, top navigation, and first test screen are confirmed. Detailed tokens, recipe layouts, image sourcing, recommendation explanation patterns, motion timing, responsive behavior, and acceptance criteria remain to resolve.
