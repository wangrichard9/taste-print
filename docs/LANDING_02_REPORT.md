# Landing 02: cleanup and immersive scale experiment

Implemented September 30, 2026, following the user's review of Landing 01. Decisions D27–D30 record the approved scope. The user likes the direction and wants to test a bigger, more immersive feel; retaining the new proportions remains a review decision.

## Result

The landing uses narrower laptop gutters, larger display type and product panels, larger food choices and illustration, and approximately screen-sized major chapters. Free scrolling remains in control. The process heading stays visible beside sequential explanations on laptops and returns to normal flow on narrower screens.

The visible motion toggle and Still/Ripple controls are removed. The system reduced-motion preference is honored automatically. Under normal motion, the food illustration itself is a native button: hovering creates ripples, and click/Enter/Space trigger one without a separate demonstration button. Reduced motion shows a static illustration. The footer's review reset becomes a regular Back to top action.

Food cards enlarge by 2.5% on pointer hover or keyboard focus. Normal motion animates the scale and a small lift over 240ms; reduced motion changes scale instantly without travel. CSS transforms preserve the grid's layout dimensions. No new library is required.

The three real preference choices, onboarding handoff, and isolated demonstration continue to use the existing flows.

## Continuation button diagnosis

The browser inspection loop reproduced the reported symptom: the native button had a gray `rgb(240, 240, 240)` background and `2px outset` border despite the intended `.text-link` styling. The same read-only computed-style assertion returned FAIL before the fix and PASS afterward. A targeted `button.text-link` reset supplies transparent background, no border, and a 44px minimum target, preserving the existing cobalt text-action treatment. The action opened onboarding and Escape dismissed it.

This simple styling bug was isolated to the real browser control; no shallow unit test was added to duplicate CSS declarations. The browser style assertion and functional click were the regression checks. No diagnostic instrumentation remains.

## Reverting size without undoing cleanup

All larger proportions live in `src/landing-immersive.css`, imported after the base landing CSS. Remove that single import from `src/components/LandingPage.tsx` to restore the earlier proportions. Keep `src/landing.css` and the current component for the cleanup, hover behavior, and native keyboard controls. The original Landing 01 screenshots are preserved.

## Verification

- Production build, including TypeScript: passed.
- Existing unit suite: 12 tests passed.
- Browser widths: 1440, 1280, 1024, 820, 390, and 320px. Each document's scroll width matched its client width.
- At 1440×900, the hero occupies the remaining 806px below the 94px header. Main text, illustration, and process pacing were inspected visually.
- Card hover changed painted width from 435px to 445.875px while layout width stayed 435px. Tab focus within the card produced the same scale.
- Continuation button appearance passed the computed-style check and opened onboarding. Keyboard dismissal worked. Test inspection/hover did not record food opinions.
- Visible motion/comparison controls are absent. The final browser follows system reduced motion and displays readable static text/illustration. The existing normal-motion shaders/choreography remain, with the ripple trigger moved onto the illustration. A separate full-motion browser run was not repeated in this reduced-motion environment.
- A page reload was needed after changing the component/import structure; transient Vite reload errors occurred while the new stylesheet was being created. The completed production build passes and the reloaded page renders the final component.

## Previews

- [Larger desktop hero](design/previews/landing-02-desktop.jpg)
- [Food choices](design/previews/landing-02-foods.jpg)
- [Taste chapter](design/previews/landing-02-scroll.jpg)
- [Phone](design/previews/landing-02-mobile.jpg)
- [Original proportions](design/previews/landing-desktop.jpg)

Review the new scale and scroll pacing before expanding motion to other app screens.
