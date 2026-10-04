# Landing 01: composed hero and motion review

Implemented September 30, 2026, under the approved landing scope in `BUILD_PLAN.md` and design decisions D14–D26. This is the first visual pass, ready for review; the illustration and exact choreography remain iterative.

## What a visitor can do

- Open the landing page at the empty hash or `#home`. Existing Discover, Your Tasteprint, and MealMerge routes remain available. The app wordmark returns home.
- Watch an approximately eight-second, labeled example: first impressions on food choices, a descriptive Tasteprint, and Discover. Manual scene buttons remain available. Example choices never enter the saved profile.
- Like or pass on three real starter recipes. These choices update the existing browser-local profile immediately and appear preselected when continuing into the six-recipe onboarding flow.
- Scroll through gradual word reveal and selective content entrances. The shared white, ink, cobalt, Inter, and control geometry are retained.
- Compare Still and Ripple versions of the authored cobalt plate illustration. Pointer interaction and a keyboard-operable “Make a ripple” button trigger distortion. Essential content and controls remain outside the canvas.
- Use reduced motion automatically when requested by the system. A temporary “Preview animations” opt-in allows explicit review of motion without changing system settings or storing a preference. Onboarding continues to follow its existing reduced-motion behavior.

## Implementation

`src/components/LandingPage.tsx` composes the page and isolates demonstration state from real preferences. Motion drives the layered hero and entrances. Adapted React Bits Scroll Reveal uses GSAP with scoped cleanup. Star Border wraps selected native buttons. Adapted Ripple Distortion uses OGL and loads separately when the illustration approaches the viewport; it pauses outside the viewport and stops rendering when waves settle. The SVG has explicit texture dimensions, the canvas retains its idle frame, and static fallback remains available when WebGL is unavailable or motion is reduced. Third-party provenance is retained in `THIRD_PARTY_NOTICES.md` and the adjacent React Bits license.

Scroll Reveal and Ripple are separate production chunks. The final build completes without the earlier chunk-size warning. This pass does not integrate recommendation experiments, a backend, accounts, group rankings, or hosting. The current browser profile still describes explicit recipe-tag counts.

## Verification

- Final `npm run build`: passed, including TypeScript.
- Final `npm test`: all 12 existing catalog/preference tests passed.
- Browser inspection at 1280×800, 1440×900, 390×844, and 320×760. The 320px document width matches its client width after the narrow overflow fix.
- Quick-start like/pass state persisted after reload and appeared in onboarding and Your Tasteprint. Temporary test choices were cleared through their normal toggle controls afterward.
- Watching the demonstration followed by reload did not create saved opinions.
- Manual preview stages and reduced-motion mode worked. Explicit full-motion preview enabled the requested effects. Scroll inspection confirmed words becoming readable progressively, rather than revealing the entire paragraph at once.
- Still removed the WebGL canvas; Ripple recreated it. Keyboard activation triggered a ripple. The graphic remained visible after waves settled and viewport sizes changed.
- Escape dismissed onboarding. Existing profile routing showed the correct choices. Native controls and focus outlines remained usable.
- No browser console errors in the final preview. Motion's expected reduced-motion notice appeared while testing the system preference.

Browser checks complement the existing unit suite; there is no newly added automated UI suite. A WebGL-unavailable device was not separately simulated; the source's guarded setup and image fallback cover that path.

## Visual review

- [Desktop hero](design/previews/landing-desktop.jpg)
- [Scroll text and food illustration](design/previews/landing-scroll-reveal.jpg)
- [Phone layout](design/previews/landing-mobile.jpg)

Review the hero's character and density, the scene transition timing, and whether the optional ripple belongs in the final landing. The scroll narrative is the main expressive moment; the plate illustration is supporting material. The current page can be tried at `http://127.0.0.1:5173/#home` while the local Vite server is running.
