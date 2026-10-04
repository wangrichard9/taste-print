# Landing 03: free scrolling and working preview

Implemented October 1, 2026 UTC, following the user's landing review. Decisions D31–D33 record the requested refinements.

## Result

The closing cobalt banner extends 16px farther on each side on laptops, with smaller extensions at narrow widths. The hero heading is approximately 4% larger. Both adjustments remain in the reversible immersive stylesheet. The reviewed food-card sizes are retained.

The Small choices process heading now scrolls normally. This removes the reported feeling of locking in place while keeping sequential explanations. The separate story's GSAP word-by-word opacity/blur reveal is retained. There is no scroll snapping, pinning, or wheel interception.

Watch the app now plays the complete 7.8-second food-choice → Tasteprint → Discover demonstration. Previously, the reduced-motion branch jumped immediately to Tasteprint and stopped playback, making the button appear inactive. That early exit is removed. The initial fix retained immediate scene changes under reduced motion; the D34 follow-up below enables the full choreography. The button shows Stop preview during playback and the description indicates Playing. Stop, replay, and manual stage navigation remain available. Demo opinions do not enter saved preferences.

## Motion preference

The first handoff retained D27's reduced-motion fallback. The user then explicitly requested removing reduced motion (D34). Landing components no longer check that preference, and landing CSS no longer suppresses the story reveal, Star Borders, or card transitions. Hero and process entrances, product-scene choreography, interactive ripples, and smooth Back to top now play normally. The illustration keeps its loading/WebGL fallback. Existing onboarding/app motion handling and system settings are unchanged.

Follow-up verification in a browser that still reports reduced motion: Star Border computed animation is `star-travel`; food cards retain their 240ms transition; the story starts at opacity 0.3 with 1px blur and reveals progressively as scrolling advances. At the end, the last word reached approximately opacity 1 and zero blur. The ripple canvas loaded successfully and the illustration button produced visible distortion. During Watch playback, the Tasteprint panel showed an intermediate transform, confirming the scene animates rather than jumping. The final production build and all 12 frontend tests passed.

## Verification

- Production build and TypeScript passed; existing frontend suite: 12 tests passed.
- Browser reproduction before the fix: clicking Watch the app immediately selected Tasteprint while the button continued to say Watch the app. After the fix: Stop preview appeared at the food-choice stage, the Tasteprint stage appeared during playback with two example likes and one pass, and Discover appeared at completion.
- Stop canceled the timers: the first stage remained selected after the original sequence would have finished. Replay restarted the sequence; selecting Discover manually canceled playback. Real food opinions remained empty throughout these checks.
- The process heading's computed position changed from sticky to static. Scrolling 360px moved its top from 302.72px to −57.28px, showing normal document flow.
- Checked 1280, 1440, 1024, 820, 390, and 320px widths. Document scroll width matched client width at each size. The closing banner retained positive outer gutters.
- Visual review at the browser's default 1280px width confirmed the larger hero and wider banner. Temporary viewport overrides were reset.
- The first handoff retained the normal-motion implementation without a full-motion run. The D34 follow-up subsequently verified the active reveal, ripple, border, and scene transitions in the same reduced-motion environment, as described above.

The deterministic browser click/state check exercised the actual preview bug. A broader hypothesis/instrumentation loop was unnecessary once the immediate reduced-motion exit reproduced the exact symptom. No diagnostic instrumentation or extra shallow unit tests were added for these limited changes.

## Previews

- [Hero](design/previews/landing-03-hero.jpg)
- [Wider closing banner](design/previews/landing-03-banner.jpg)
- [Restored scroll blur and food illustration](design/previews/landing-03-motion.jpg)

Review these small refinements before proposing further landing content or broader app motion.
