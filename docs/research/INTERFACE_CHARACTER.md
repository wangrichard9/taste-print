# Interface character: Ingredients and MealMerge

Researched 2026-10-02. Discussion only. **Every Tasteprint change below is proposed and unapproved.** This note changes no app code, design standards, or recorded decisions.

## Question and constraints

The user finds Ingredients and MealMerge formulaic and corporate: repeated marketing headings, prose, boxes, and text. The goal is a more authored food experience within the confirmed quiet editorial foundation: white canvas, ink text, crisp cobalt, restrained sans-serif typography, modest rounding, food photography, and selective motion. Preserve honest ingredient matches, local guest identity, and supported recommendation evidence. Read `PROJECT_BRIEF.md`, `design/DESIGN_STANDARDS.md`, `design/DECISIONS.md`, and `COLLABORATION.md` before this research.

## Three primary references

### Duolingo: a shared visual grammar

**Evidence.** Duolingo describes constructing its human characters from Duo's simple geometric design language so they belong to the same visual world. It chose relatable modern humans with quirky personalities after rejecting concepts too far from language learning. Its characters also appear inside exercises and react to correct answers. These are stated design choices, not evidence that a mascot would improve Tasteprint. [Duolingo: Building character](https://blog.duolingo.com/building-character/)

**Our interpretation — proposed.** Character can come from a consistent family of shapes and small contextual behaviors. Tasteprint could use an oval potato/plate, a wedge, a leaf, and a noodle curl in one recognizable graphic vocabulary. A slightly offset leaf or unexpected crop can add wit without requiring a cast of mascots. Use the same grammar in navigation previews and task screens, with different compositions for each task.

### Headspace: simple metaphors with restraint

**Evidence.** Headspace's own hosted illustration guidelines advocate simple palettes, flat color, thoughtful metaphors, and dramatic scale contrast. Core shapes underpin its illustrations; shapes can frame photography, and sprites can connect photographs with illustrations. It warns against busy illustrations and overusing faces. [Headspace illustration guidelines](https://live.standards.site/headspace/illustration)

**Our interpretation — proposed.** Borrow the compositional discipline, not Headspace's faces, orange palette, or emotional vocabulary. One food-related composition beside the working controls could do more than another introductory paragraph. Keep cobalt and ink graphic elements on white; actual recipe photography can supply natural color. Scale and cropping can create personality while the controls remain familiar.

### GOV.UK: remove the need for explanations

**Evidence.** GOV.UK advises considering interface improvements before adding words, starting with less help text, keeping copy short and direct, placing important words first, and making headings describe their purpose. It also requires associated labels and warns against communicating by shape or color alone. This is a clarity reference, not Tasteprint's aesthetic or full tone model. [GOV.UK: Writing for user interfaces](https://www.gov.uk/service-manual/design/writing-for-user-interfaces)

**Our interpretation — proposed.** Replace repeated product pitches with a concrete question and an immediately usable control. Keep ingredient-rule caveats, evidence gaps, and local-storage facts near the action or result they qualify. Reducing prose must not conceal how matching works or what a guest profile represents.

## Original food motifs to discuss

All options below are **proposed/unapproved**, not selected directions.

| Screen | Proposed composition | What the person does |
| --- | --- | --- |
| Ingredients | A loose preparation surface: a large cropped cobalt plate arc, two or three geometric ingredient shapes, and entered ingredient names arranged neatly alongside the input. Thin rules divide results rather than boxing every section. | Answer “What's on hand?”, add ingredients, then “Find recipes”. If shapes respond to entry, they acknowledge an action; they do not claim recognition of an ingredient the matcher cannot support. |
| MealMerge | A small overhead table scene: one shared plate and 2–4 named place settings for the current person and real local guests. Add guest remains an ordinary labeled button. Guest editing opens from each named setting. | Answer “Who's eating?”, edit each person's choices, then “Find a meal”. Place settings describe group membership, not predicted satisfaction. |
| Shared details | A compact ink/cobalt food sketch in empty states or a small edge detail, with deliberate asymmetry and a single consistent stroke/fill treatment. | Understand an empty state through a direct next action; keep actual recipe images and evidence dominant after results arrive. |

**Recommendation — proposed.** First discuss a paired Ingredients/MealMerge composition with shorter task copy, fewer enclosing boxes, and one original food graphic per screen. Review a static comparison before choosing illustration strength or motion. Judge whether the first action is obvious, the two screens feel distinct, the food theme is recognizable at a glance, and evidence remains clear. No new animation engine, model behavior, palette, mascot, or implementation is approved by this note.

Source access note: the former Duolingo shape-language URL redirects to its design blog, so this note uses the first-party character article instead. Headspace's illustration page was readable in search-indexed content; direct page extraction returned no text. No secondary design summaries were used as evidence.
