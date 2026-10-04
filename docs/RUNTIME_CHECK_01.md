# Runtime recovery and recipe-card check

Checked October 1, 2026, following the user's request to restore loading and test dish-card effects.

## Loading failure and recovery

The backend was already running: `/api/health` returned revision `build05`, all 5,006 recipes, and Discover/Ingredients/MealMerge support. A real Discover request through port 5173 returned shared-like results. No training, model artifact change, or backend restart was necessary.

The development page repeatedly rendered an empty React root. Requests for its referenced React and ReactDOM dependency URLs returned **504 Outdated Optimize Dep**, even while HTML and source-module requests returned 200. Restarted only the verified Vite frontend with `--force`. The newly referenced React, ReactDOM and JSX runtime dependencies then returned 200, and the browser rendered 24 recipe cards with the existing person's two-like shared-like ranking.

The prior production preview on 5174 had a separate 403 caused by the service's existing app-origin allowlist. Relaunched that preview on its configured, permitted port **4173**. A request with the 4173 browser origin and a known liked recipe returned 5,005 unseen results, including 3,505 with shared-like evidence. The allowlist was not broadened.

## Recipe-card verification

Actual pointer exploration of Bourbon Chicken's image registered `:hover`. Its computed transform remained `none` and transition duration `0s`, consistent with the existing reduced-motion rule on this device. The photo's existing normal-motion effect is a 2.5% image zoom; whole-card expansion is not currently implemented. Asked whether the user wants the recipe-hover scope to always animate as navigation does; no policy change was assumed during this check.

Pointer exploration of the recipe title changed its computed text color to cobalt (`rgb(38, 71, 235)`). Opening the image displayed the real recipe dialog; its source directions loaded from the backend. Closing returned to Discover. No opinions, saves or guests were edited, and no browser error logs were reported.

The full frontend suite with `VITE_TASTEPRINT_LIVE_TEST=1` passed **68 tests across 15 files**, including real Ingredients and MealMerge API/decoder checks. No application source was changed, so no new production build was needed. The runtime HTTP/browser reproduction serves as the verification for this generated-cache failure; no artificial unit regression was added.

Running after recovery: model 8000, development app 5173, production preview 4173. The retired preview URL on 5174 is no longer served. Both frontend processes were launched hidden through the terminal tooling.
