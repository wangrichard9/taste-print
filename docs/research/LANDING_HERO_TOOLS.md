# Landing hero graphics and motion: quick research

Researched September 30, 2026. Scope: a short primary-source scan of practical creation workflows, not a popularity survey or an inspection of how the gallery websites were built. No tools installed or product code changed.

## Recommendation for Tasteprint

Proceed with the accepted option A: one authored composition of readable product panels, supporting food photography, and an animated relationship between a food choice and the visible Tasteprint. Build the panels in React/CSS, use SVG for small bespoke diagram details, and animate the scene with the existing Motion engine. This is a design recommendation based on the agreed product behavior, not a claim that a particular reference site uses this stack.

The important distinction is **what creates the visual** versus **what moves it**. A product composition can be ordinary React markup and CSS. SVG supplies scalable custom shapes. Photography supplies texture. Motion or GSAP choreographs those pieces; choosing an engine does not supply the finished hero artwork. Designer-authored vector or 3D assets use separate editors and web runtimes.

## Choices to browse

For visual browsing first: [React Bits Stack](https://www.reactbits.dev/components/stack), [Scroll Reveal](https://www.reactbits.dev/text-animations/scroll-reveal), and [Animated Content](https://www.reactbits.dev/animations/animated-content) provide specific live component demos. [Rive Marketplace](https://rive.app/marketplace/) has a searchable featured/latest collection (JavaScript required). [Spline Community](https://community.spline.design/) provides ready-made 3D templates and remixable projects. Browse for a movement or composition to adapt; an external asset would need its own usage terms checked before adoption.

| Route | What it produces and how it works | Tasteprint fit and tradeoff |
| --- | --- | --- |
| **Custom React/CSS/SVG + [Motion scroll examples](https://motion.dev/docs/react-scroll-animations)** | Motion supports viewport-triggered entrances and scroll-linked transforms, parallax, image reveals, and sticky-section walkthroughs. Its guide includes live examples and source. | Best first fit: readable app panels can share the app's styling and update from real choices. Requires composing the artwork and choreography ourselves; that authorship is what gives it identity. |
| **[GSAP ScrollTrigger](https://gsap.com/docs/v3/Plugins/ScrollTrigger/)** | Connects a tween or timeline to scrolling; supports pinning, scrubbing, and snapping. | Consider if the selected walkthrough needs a carefully coordinated timeline. Motion already handles the initial planned effects, so adding both engines is not required. |
| **[React Bits](https://www.reactbits.dev/get-started/index)** | Browse live component demos and adapt their source. Useful candidates: [Scroll Reveal](https://www.reactbits.dev/text-animations/scroll-reveal), [Animated Content](https://www.reactbits.dev/animations/animated-content), and [Stack](https://www.reactbits.dev/components/stack). | Scroll Reveal can pace one short explanatory line; Animated Content can introduce panels; Stack suggests a layered food-choice composition. These are ingredients for the design, not a complete hero. |
| **[Rive state machines](https://rive.app/docs/editor/state-machine/state-machine)** | Visual states and transitions connect animations into interactive motion graphics for websites and apps. Artwork/animation is authored in the [Rive editor](https://rive.app/editor). | Useful for a custom vector symbol that reacts to hover, clicks, or preference state. Adds a separate asset-authoring workflow; the ordinary app panels can stay in React. |
| **[Lottie Creator](https://lottiefiles.com/lottie-creator)** | Browser-based keyframe editor with SVG import and Lottie/dotLottie export; also supports interactive state-machine workflows. | Useful for a small branded illustration or a authored demonstration. Real controls and changing profile content are easier to maintain in the app's own components; Lottie is not limited to passive loops. |
| **[After Effects → Lottie](https://lottiefiles.com/plugins/after-effects)** | Author an animation in After Effects, export Lottie JSON/dotLottie with the plugin, preview, and test feature compatibility for the intended player. | An alternative when an animator already works in After Effects. Exported animations need compatibility checking; no reason to add this production workflow for the first React hero. |
| **[Spline web experiences](https://spline.design/solutions/3d-web-experiences)** | Create materials, lighting, animation, and interactions in a 3D scene, then embed/export it for the web. The page links community templates and examples. | Suitable if we deliberately choose a sculptural 3D brand object. Current option A does not need one; authoring and validating a separate scene adds work without resolving the product story. |
| **[Lucide React](https://lucide.dev/guide/react)** | Small customizable inline-SVG icons, imported individually as React components. | Reuse the existing icon language for hearts, playback, arrows, and controls. An icon set supports the hero rather than supplying its signature graphic. |

## React Bits implementation details verified in official source

- [Scroll Reveal source](https://github.com/DavidHDev/react-bits/blob/main/src/content/TextAnimations/ScrollReveal/ScrollReveal.jsx) uses GSAP/ScrollTrigger for scroll-linked rotation, word opacity, and optional blur. Its stock cleanup kills all ScrollTriggers, so adopting it requires local lifecycle cleanup; do not paste unchanged into a page with other triggers.
- [Animated Content source](https://github.com/DavidHDev/react-bits/blob/main/src/content/Animations/AnimatedContent/AnimatedContent.jsx) uses GSAP/ScrollTrigger for an entrance with configurable distance, direction, scale, opacity, timing, and delay.
- [Stack source](https://github.com/DavidHDev/react-bits/blob/main/src/content/Components/Stack/Stack.jsx) uses `motion/react` for draggable layered cards; it supports click-to-back and autoplay. The stock action reorders cards, so liking or skipping foods still requires Tasteprint logic and explicit accessible controls.

These are current repository-source observations, not a guarantee that every language/styling variant is identical. Adapt selected sources for keyboard access, reduced motion, shared tokens, and lifecycle behavior. Preserve notices under the project's existing React Bits adoption practice.

## Proposed first scene

### Follow-up shortlist after user review

The user favors Card Swap and especially Scroll Reveal, and rejects the reviewed Stack and Scroll Stack treatments. Two further graphical candidates were checked in live official previews:

- [React Bits Scroll Expand](https://www.reactbits.dev/animations/scroll-expand): a compact media frame grows to occupy the stage as the user scrolls, with its heading lifting away and content appearing over the enlarged scene. Scroll inside the demo frame. A Tasteprint adaptation would apply this movement to the app composition rather than large food photography. This is a proposed custom adaptation; the stock component's media API is not an implementation of interactive product panels.
- [Motion Scroll Image Reveal live demo](https://examples.motion.dev/react/scroll-image-reveal), with [official explanation](https://motion.dev/examples/react-scroll-image-reveal): an image's clip mask opens from the center while the image shifts subtly with scroll. A Tasteprint adaptation could reveal parts of a product preview in place. The free scroll-animation guide already demonstrates the underlying clip-path technique; the premium example's complete source is not required to explore that effect.

These are alternatives for review, not approved adoption. Option A remains the accepted signature form.

1. A large Tasteprint panel provides the recognizable silhouette; a smaller offset food-choice panel overlaps its edge.
2. The panels arrive with a deliberate stagger; photographs remain supporting elements rather than a food collage.
3. “Try three foods” switches the composition to real inputs. “Watch the app” plays clearly labeled sample selections through the same scene, without writing demonstration choices to the visitor's saved preferences.
4. The lower walkthrough reuses those panels, revealing selection, supported taste patterns, and discovery in stages while the visitor controls scrolling.

This choreography remains a proposal for visual review. The current instructions are sufficient to make a first motion study; more references would help only if the user wants a particular movement or illustration style. No custom 3D asset, paid animation pack, or additional engine is necessary to begin.
