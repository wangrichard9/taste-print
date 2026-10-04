import { useEffect, useState } from 'react';
import { recipeChoices } from './discovery';
import { parseIngredientResult, type IngredientRequest, type IngredientResult } from './ingredients';
import type { TasteState } from './taste';

type State = { key: string; status: 'idle' | 'loading' | 'ready' | 'error' | 'invalid'; result: IngredientResult | null };

export function useIngredientRecommendations(request: IngredientRequest | null, taste: TasteState) {
  const key = request ? JSON.stringify({ ...request, ...recipeChoices(taste) }) : '';
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState<State>({ key: '', status: 'idle', result: null });
  useEffect(() => {
    if (!request) { setState({ key: '', status: 'idle', result: null }); return; }
    const controller = new AbortController();
    let cancelled = false;
    let timedOut = false;
    let invalid = false;
    setState({ key, status: 'loading', result: null });
    const timeout = window.setTimeout(() => { timedOut = true; controller.abort(); }, 10000);
    const debounce = window.setTimeout(async () => {
      try {
        const response = await fetch('/api/ingredients', { method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: key, signal: controller.signal });
        if (!response.ok) { invalid = response.status === 400; throw new Error('Ingredient request failed'); }
        const result = parseIngredientResult(await response.json(), request, taste);
        if (!cancelled && !controller.signal.aborted) setState({ key, status: 'ready', result });
      } catch {
        if (!cancelled && (!controller.signal.aborted || timedOut)) setState({ key, status: invalid ? 'invalid' : 'error', result: null });
      } finally { window.clearTimeout(timeout); }
    }, 180);
    return () => { cancelled = true; controller.abort(); window.clearTimeout(timeout); window.clearTimeout(debounce); };
    // Request contents and explicit choices drive ranking, never saves.
  }, [key, attempt]);
  return { ...(key ? state.key === key ? state : { key, status: 'loading' as const, result: null }
    : { key, status: 'idle' as const, result: null }), retry: () => setAttempt(value => value + 1) };
}
