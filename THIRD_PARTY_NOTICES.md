# Third-party notices

## React Bits Stepper

`src/components/react-bits/Stepper.tsx` is adapted from the [React Bits TypeScript Stepper](https://github.com/DavidHDev/react-bits/blob/main/src/ts-default/Components/Stepper/Stepper.tsx), inspected 2026-09-30. Copyright (c) 2026 David Haz. The supplied MIT + Commons Clause license is retained verbatim in `src/components/react-bits/LICENSE.md`.

Changes include Tasteprint styling, shorter transitions, reduced-motion support, native keyboard-operable buttons, backward-only indicator navigation, final-step validation, resize-aware content measurement, and step-heading focus. Motion is its animation dependency; React Bits is copied/adapted source, not a package dependency.

## Provisional photography

Historical Build 01 only: the provisional photos described below are no longer used by the current catalog.

The two original preview photos are linked from the [Omnifood sample repository](https://github.com/DarshanVaishya/omnifood/tree/master/img/meals). Additional illustrative food photos are linked from Unsplash's image host. Exact URLs are stored in `src/data/catalog.ts` alongside source links. These photos depict dish concepts, not verified recipes. Ingredients and tags are hand-authored sample metadata.

These are provisional UI-testing sources. Production redistribution rights and photographer attribution have not been audited. Do not treat these notices as a completed image-license review. Before publishing, replace/audit the photo set with documented rights and verify recipe/image matching. The app provides a missing-image fallback and does not download/repackage these photos.

## Local research dataset

The approved local audit uses [Food.com Recipes and Reviews](https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews), uploaded by `irkaal`, version 2. Underlying recipe/review content originates from Food.com contributors; linked photos are hosted at `img.sndimg.com`. The uploader's license label is **CC0: Public Domain**; this is recorded attribution and stated provenance, not an independent determination of all contributor/photo rights.

Files were retrieved September 30, 2026 (local time), without credentials, for a temporary local Tasteprint demo/audit. Raw data and the draft review catalog are not bundled into the frontend and are ignored by version control. Source URLs, version, exact sizes, retrieval time, and SHA-256 hashes are recorded in `data/raw/foodcom-v2/manifest.json`. See [audit report](docs/DATA_AUDIT_01.md). No claim of original authorship of the dataset or photos is made. Revisit usage requirements if publication scope changes.

Build 02 bundles metadata and directions for 30 explicitly selected recipes in `src/data/recipes.json`; it does not bundle the bulk dataset, reviewers, review text, historical user IDs, or downloaded photos. `data/catalog-selection.json` records source IDs, editorial presentation and chosen photo indexes. Each recipe detail links to its original recipe/photo source and the dataset. Photographs load online directly from `img.sndimg.com`. Photo contributors have not been individually identified for every image; source linking is not represented as a complete contributor-permission audit. Selection and image review are documented in [Build 02 report](docs/BUILD_02_REPORT.md).

## Reused embedding model (ML 01)

The local content experiment reuses [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`. The provider's model card labels the model Apache-2.0 and identifies it as a generic sentence/short-paragraph encoder. Downloaded model/license files remain in the ignored local model cache. Tasteprint does not claim to have trained or fine-tuned its weights. See [ML 01 protocol](docs/ML_01_PROTOCOL.md) for exact reuse, fitting-data rules, and evaluation limitations. Python dependencies are pinned in `requirements-ml.txt`, with license files retained in installed packages; CPU-only PyTorch is installed from its official wheel index.

## React Bits landing animations

The landing page adapts [Scroll Reveal](https://github.com/DavidHDev/react-bits/blob/main/src/ts-default/TextAnimations/ScrollReveal/ScrollReveal.tsx), [Star Border](https://github.com/DavidHDev/react-bits/blob/main/src/ts-default/Animations/StarBorder/StarBorder.tsx), and [Ripple Distortion](https://github.com/DavidHDev/react-bits/blob/main/src/ts-default/Animations/RippleDistortion/RippleDistortion.tsx), inspected 2026-10-01. Copyright (c) 2026 David Haz. The supplied license is retained in `src/components/react-bits/LICENSE.md`. Scroll Reveal uses scoped GSAP cleanup. Star Border wraps native controls. Ripple adds a static loading/WebGL fallback, local pointer handling, a keyboard trigger, and rendering only while visible and active. Landing reduced-motion suppression was subsequently removed at the user's explicit request (D34). The layered hero is custom Motion code inspired by the compositional idea of Card Swap, rather than copied Card Swap source. The plate graphic is authored SVG.

## React Bits Tilted Card (UI 04)

`src/components/react-bits/TiltedCard.tsx` adapts the [React Bits TypeScript Tilted Card](https://github.com/DavidHDev/react-bits/blob/main/src/ts-default/Components/TiltedCard/TiltedCard.tsx), inspected October 1, 2026. Copyright (c) 2026 David Haz. The existing MIT + Commons Clause notice in `src/components/react-bits/LICENSE.md` applies. The adaptation accepts children to preserve real recipe photos/fallbacks and native controls, limits tilt to four degrees and scale to 1.015, adds keyboard focus feedback, and keeps touch/reduced-motion static. Motion was already installed; no new package dependency is added.

## Package dependencies

React, Vite, Motion, GSAP, OGL, Lucide, Inter, TypeScript, and Vitest are installed through npm. Exact resolved dependencies are tracked in `package-lock.json`; package license files remain in their installed packages. Inter font files are bundled locally at build time.
