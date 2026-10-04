# Design decisions

Updated: 2026-09-30. Status: accepted foundation implemented; details remain iterative.

## Confirmed

| Choice | Evidence |
| --- | --- |
| Modern app with an intentional, authored feel | Explicit user request |
| References guide the direction | User describes them as references and direction |
| Buena typography and layout deserve particular attention | Explicit user preference |
| Explore React Bits | Explicit user request; component selection remains open |
| Establish Markdown guidance alongside the design discussion | Explicit user request |

## Round 1: resolved foundational choices

| ID | Decision | Chosen direction | Reason | Status |
| --- | --- | --- | --- | --- |
| D01 | Main visual direction | Quiet editorial with visual studio energy; food magazine rejected | Explicit user choice | Confirmed |
| D02 | Meaning of an unwanted generic look | Glowing gradients, generic typography, cheap/inconsistent imagery, and an overall formulaic feel | User identifies these as the main objections; do not infer that every card or rounded button is rejected | Confirmed |
| D03 | Main usage context | Laptop-first; phone usability receives limited attention in the initial build | First build and demo are based on laptop usage | Confirmed |
| D04 | Scope of the design language | More expressive landing page with a coherent shared identity with the app | Stand out without creating a visual disconnect | Confirmed |
| D05 | Motion appetite | Selective motion | Explicit user choice of the middle option | Confirmed |
| D06 | Overall color mood | Bold, crisp, less cozy; reject the warm food-magazine palette | Explicit user preference; exact palette still open | Confirmed |

## Round 2: resolved visual foundations

The user accepted all recommendations for Q6–Q10, with an explicit white-background clarification.

| ID | Decision | Chosen direction | Reason | Status |
| --- | --- | --- | --- | --- |
| D07 | Accent palette and neutral temperature | White canvas, dark text, cobalt accents | User accepts cobalt and specifically requests a white background rather than ink | Confirmed |
| D08 | Typography treatment | Restrained app typography with larger, bolder landing display type; one shared family initially | User accepts the recommendation | Confirmed |
| D09 | Component geometry | Modest control rounding with crisper imagery and layouts | User accepts the recommendation; exact radius tokens still need validation | Confirmed |
| D10 | Laptop app shell | Compact top navigation | User accepts the recommendation | Confirmed |
| D11 | First full-screen design test | Discovery | User accepts the recommendation and asks to see the white-and-cobalt treatment | Confirmed |

## Build authorization

| ID | Decision | Chosen direction | Reason | Status |
| --- | --- | --- | --- | --- |
| D12 | Move from preview to implementation | Build the white-and-cobalt app; refine smaller UI parts as we go | User prefers the white preview, calls the overall direction desirable but unfinished, and explicitly asks to start building | Confirmed |
| D13 | Build communication | Explain milestones and actionable user steps, especially before ML work | Explicit user request | Confirmed |

Build 01 implements discovery, preference onboarding, and a descriptive local Tasteprint. Inter, exact tokens, six seed dishes, and Stepper adaptations are implementation choices under the accepted direction, open to refinement. They do not establish dataset selection, model outputs, final MVP scope, or production photo licensing.

## Landing page: direction and quick-start review

Confirmed in conversation on 2026-09-30. The user wants to compare quick-start alternatives before selecting the interaction.

| ID | Decision | Chosen direction | Reason | Status |
| --- | --- | --- | --- | --- |
| D14 | Landing story | Lead with finding food and enjoyment; understanding taste is the underlying idea | User wants both the immediate food benefit and Tasteprint's distinguishing concept | Confirmed |
| D15 | Hero balance | Mix a readable app/profile preview with supporting food imagery; photography must not dominate | User explicitly accepts a mixture and limits image prominence | Confirmed |
| D16 | First motion scope | Landing page and reusable animation components first; broader app motion follows review | User accepts the recommended scope | Confirmed |
| D17 | Motion direction | Expressive landing motion, including gradual scroll storytelling; preserve the shared design identity | User's Airvoir reference and explicit request for animation | Confirmed direction; detailed sequence remains proposed |
| D18 | Quick-start interaction | Include both trying three foods and watching an animated app demonstration | After reviewing alternatives, user says both are important | Confirmed; placement and detailed behavior remain open |
| D19 | Landing composition review | Develop a fuller, more expressive composition with meaningful animated app previews | User finds the entry-flow comparison empty and requests further discussion of how to fill the space | Confirmed refinement direction; detailed composition remains proposed |
| D20 | Hero visual anchor | Give the landing page one recognizable signature graphic or composed product element | User supplies a landing-page gallery and explicitly asks for an element that creates the landing-page feel | Confirmed requirement; visual form and choreography remain open |
| D21 | Signature visual form | Option A: a composed product scene showing food choices becoming a descriptive Tasteprint | User explicitly says to try option A, then requests a quick tooling research pass while retaining that choice | Confirmed; choreography and first implementation remain iterative |
| D22 | Reviewed motion examples | Favor Card Swap and especially Scroll Reveal; decline the reviewed Stack and Scroll Stack treatments | User identifies 1 and 4 as favorites and dislikes the popping/stacked feel of 2 and 3 | Confirmed preference; exact adoption remains open |
| D23 | Next motion comparison | Do not use Scroll Expand or curtain reveal as the main scene treatment | User feels no particular excitement for either A or B | Declined for this pass |
| D24 | Ripple graphic | Try React Bits Ripple Distortion on a supporting food illustration, independently reviewable | User requests seeing it and says not to force it into the layout | Approved experiment; final retention remains open |
| D25 | Star Borders | Try restrained Star Borders on selected landing controls | Explicit user request; a scoped exception to the earlier decorative-glow exclusion | Approved for landing controls only |
| D26 | Begin landing implementation | Implement option A, slow text reveal, selective text/scene motion, a working food trial and isolated app demonstration | User explicitly requests implementing text and planned compatible animations | Approved first pass; visual details remain iterative |
| D27 | Remove review controls | Remove the visible motion toggle and Still/Ripple comparison controls; initially keep automatic system reduced-motion support | User likes the first pass and requests removing these small controls | Controls remain removed; motion policy superseded by D34 |
| D28 | Immersive scale | Try larger type, product scene, recipe cards, and illustration with narrower outer margins and approximately screen-sized chapters | User explicitly requests testing a bigger feel and wants the option to revert | Approved reversible experiment; final proportions remain open |
| D29 | Continuation action | Reset native button chrome so Continue with my taste matches the existing action styling | User reports the action looks unrendered; browser inspection reproduces gray background and outset border | Confirmed fix |
| D30 | Card hover | Try a small enlargement on landing food-card hover and keyboard focus, with reduced-motion adaptation | User explicitly wants to see the hover feel | Approved experiment |
| D31 | Free process scrolling | Remove the sticky process heading while retaining sequential content and the story's scroll reveal | User reports the Small choices heading feels locked while scrolling | Confirmed fix |
| D32 | Small scale refinements | Widen the closing cobalt banner slightly and increase the hero heading modestly; retain the reviewed food-card sizing | User likes the current page and requests these limited size changes | Confirmed refinement |
| D33 | Working app demonstration | Keep the timed food-choice → Tasteprint → Discover sequence available with reduced motion, using immediate scene changes in that mode | User reports Watch the app seems inactive; reduced motion was ending the demonstration immediately | Confirmed fix |
| D34 | Landing motion always enabled | Remove landing reduced-motion branches and CSS suppression so story blur, ripple, Star Borders, hero/section entrances, scene transitions, and card feedback play normally | User explicitly says get rid of the reduced motion after the fallback explanation | Confirmed; supersedes D27's landing motion policy |

Airvoir is a pacing and composition reference, not a requirement to copy its imagery or long scroll distances. The first landing implementation uses Motion for the composed hero and selective entrances, adapted GSAP Scroll Reveal for the gradual text, and React Bits Star Border and Ripple Distortion for the requested experiments. Real quick-start choices persist through existing onboarding; the labeled demonstration is isolated from the profile. Still/Ripple controls support review. Reduced motion is the default when requested by the system; a visitor can explicitly opt into a temporary animation preview. Final visual retention and choreography remain iterative. See `docs/LANDING_01_REPORT.md` for behavior and verification.

Landing 02 supersedes the first pass's visible review controls: reduced motion is automatic, the illustration owns its ripple interaction, and the larger proportions are isolated in `src/landing-immersive.css` for reversal. Food-card hover and keyboard focus use a restrained enlargement. See `docs/LANDING_02_REPORT.md` for the continuation-button diagnosis, verification, and comparison images. Final scale and timing remain open for review.

Landing 03 removes the sticky process heading, slightly enlarges the hero text, widens the closing banner, and fixes the complete demonstration. The follow-up D34 resolves the motion question: landing animations now play normally regardless of the system reduced-motion flag. See `docs/LANDING_03_REPORT.md` for verification.

## Build 02 data presentation

| ID | Decision | Chosen direction | Reason | Status |
| --- | --- | --- | --- | --- |
| D14 | Next bounded build | Approximately 30 reviewed real recipes in the existing app, before recommendation experiments | User accepted Q1 recommendation | Confirmed |
| D15 | Photo delivery | Online-linked recipe photos; offline caching is not a priority | User explicitly declined offline-demo priority | Confirmed |

Build 02 retains the white/cobalt layout and six starter choices. Source ingredients/directions are distinguished from editorial names, descriptions, and taste tags. Recipe/photo-source and dataset links appear in details. A small local JSON catalog is not a trained recommender.

## Feature screen placeholders

| ID | Decision | Chosen direction | Reason | Status |
| --- | --- | --- | --- | --- |
| D35 | Build feature UI before engine integration | Expand Your Tasteprint and MealMerge; add ingredient-entry navigation and sample recipe results | User explicitly requests components, navigation, and placeholders while another agent researches the process | Approved UI-only scope |
| D36 | Placeholder evidence | Separate example profiles and fixed recipe/group results from saved choices; label them as samples without invented match percentages | User requests placeholders rather than real matching or machine-learning functionality | Confirmed |
| D37 | Feature design maturity | Use current app standards for a coherent first pass; revisit detailed interactions and design through later user sessions | User explicitly defers detailed design agreements | Provisional implementation; final layouts open |

UI 03 implements these screens; `docs/UI_03_REPORT.md` records the working interactions, fixture limitations, and visual previews.

## Discover integration

| ID | Decision | Chosen direction | Reason | Status |
| --- | --- | --- | --- | --- |
| D38 | Live Discover evidence and catalog | Expand to 5,006 model recipes; distinguish shared-like ranking, popularity fallback and unavailable service; label bulk source metadata and preserve photo fallback | User approved the concrete integration scope October 1 and wants to move beyond algorithm experiments | Confirmed; verification recorded in Build 03 report |

No new visual direction or motion component is selected here. Landing previews and feature fixtures remain illustrative; only Discover is connected to the model.

## Ingredient integration

| ID | Decision | Chosen direction | Reason | Status |
| --- | --- | --- | --- | --- |
| D39 | Live ingredient options | Keep the white/cobalt layout and three priorities, balanced by default. Allow extra ingredients and already-liked recipes, but separate new ideas from known favorites. Show actual matched source names and other listed ingredients; exclude passed recipes | User approved connecting Ingredients and emphasized multiple choices and discovery, not a shortlist limited to favorites | Confirmed October 1; replaces the Ingredients-only sample requirement from D36/D38 |

No new visual direction, motion library, dietary constraint, substitution system or model training was approved. MealMerge and the landing/profile sample scenes remain illustrative. New-to-likes is not evidence of niche discovery or improved recommendation quality.

## MealMerge integration

| ID | Decision | Chosen direction | Reason | Status |
| --- | --- | --- | --- | --- |
| D40 | Real local group flow | Current Tasteprint plus 1–3 editable local guests; Balanced compromise default and Overall appeal comparison; actual per-person evidence and real source recipes, without invented satisfaction percentages | User explicitly approved this bounded scope after reviewing Ingredients and the group-policy proposal | Confirmed; replaces the MealMerge-only sample requirement in D36/D38/D39 |

Preserve the existing editorial layout and native controls. Guest records are separate from personal preferences; missing evidence is unknown, not rejection. Broader evidence leads both policies, which compare supported relative ranking positions. No ingredient/group safety filter, accounts, invitations, new training or final evaluation is included. Landing and profile demonstration scenes remain labeled examples.

## Tasteprint sensory display (UI 04)

| ID | Decision | Chosen direction | Reason | Status |
| --- | --- | --- | --- | --- |
| D41 | Controlled sensory vocabulary | Adopt the 18 definitions proposed in `research/TASTE_VOCABULARY.md`, with stable IDs and separated taste/aroma/texture/chemical-sensation groups | User explicitly accepts the definitions and wants a consistent basis for the graphics | Confirmed October 1 |
| D42 | Two complementary graphics | A separate five-basic-taste wheel with varying petal sizes, plus an interactive constellation of the controlled vocabulary | User likes both directions and assigns each a specific role | Approved implementation; proportions and choreography iterative |
| D43 | Profile motion | Existing Motion for selection/path/state feedback; try an adapted React Bits Tilted Card on supporting recipe images | User asks to implement appropriate animation/design and previously likes these components | Approved scoped experiment |
| D44 | Diagram hover exploration | Lift wheel sections without changing petal radius, preview definitions on hover/focus, and highlight constellation connections with a brief travelling dot and selection ripple | User explicitly requests more animations and hovers on the graphics, especially each wheel section | Approved October 1; motion strength remains iterative |

Wheel size counts liked recipes carrying each authored, metadata-estimated note, not sensory intensity or liking probability. Missing notes remain unassessed. The first annotation set covers the 30 reviewed recipes; bulk categories are not sensory evidence. Keep real choices, source metadata, example-profile isolation and all recommendation engines intact. A grilling round is optional after reviewing the implemented design, not a prerequisite the user imposed.

## App navigation motion (UI 05)

| ID | Decision | Chosen direction | Reason | Status |
| --- | --- | --- | --- | --- |
| D45 | Approved navigation package | Travelling highlight, page arrival sequence, gliding Tasteprint view tabs and responsive navigation tiles (options 1, 2 and 4) | User explicitly chooses this package for now after considering recipe expansion and other options | Approved October 1; recipe-card expansion and other options remain later proposals |
| D46 | Navbar reference | Adapt AccessGrid's compact floating bar and changing illustrated panels into direct Tasteprint destination links with lightweight hover/focus graphic previews | User explicitly supplies AccessGrid as navbar design/animation inspiration; inspected October 1 | Approved inspiration; exact composition and choreography iterative |
| D47 | Navigation motion preference | Always show this navigation package's animations, including destination graphics, page arrivals, gliding local tabs and responsive navigation tiles | User explicitly selects Always show the navigation animations after being told the preview browser requests reduced motion | Confirmed October 1; scoped override, not a change to diagram/onboarding motion |

Keep the app's white/ink/cobalt identity, native hash links, keyboard and touch access, and existing state/engines. Graphic previews describe destinations, not inferred user taste or model evidence. No additional navigation hierarchy or settings are implied by the reference.

## Discover refresh (October 4)

| ID | Decision | Chosen direction | Reason | Status |
| --- | --- | --- | --- | --- |
| D48 | Explicit recommendation refresh | Keep automatic updates and add an always-visible Refresh recommendations button above the Discover filters, with disabled/loading feedback and the successful completion time. Preserve the active search/filter and actual model order | User reports All dishes appears unchanged after likes and explicitly requests a refresh control; make request completion visible without promising a different ranking | Confirmed October 4 |

## Further design rounds

After Round 2, resolve detailed tokens, discovery and comparison patterns, imagery conventions, interaction details, and observable design acceptance criteria. Sequence questions by dependency rather than locking every choice at once.

Record accepted choices here with a short reason and the affected standard. Keep the full rules in `DESIGN_STANDARDS.md` rather than duplicating them in this log.
