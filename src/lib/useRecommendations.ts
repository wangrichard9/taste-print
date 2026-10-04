import { useEffect, useState } from 'react';
import { parseRecommendations, recipeChoices, type RecommendationResult } from './discovery';
import type { TasteState } from './taste';

type State = { key: string; attempt: number; status: 'loading' | 'ready' | 'error';
  result: RecommendationResult | null; updatedAt: number | null };

export function useRecommendations(taste: TasteState, active: boolean) {
  const key = JSON.stringify(recipeChoices(taste));
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState<State>({ key: '', attempt: -1, status: 'loading', result: null, updatedAt: null });
  useEffect(() => {
    if (!active) return;
    const controller = new AbortController();
    let timedOut = false;
    let cancelled = false;
    setState({ key, attempt, status: 'loading', result: null, updatedAt: null });
    const timeout = window.setTimeout(() => { timedOut = true; controller.abort(); }, 10000);
    const debounce = window.setTimeout(async () => {
      try {
        const response = await fetch('/api/recommendations', { method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: key, signal: controller.signal });
        if (!response.ok) throw new Error('Local recommendation service unavailable');
        const result = parseRecommendations(await response.json(), taste);
        if (!cancelled && !controller.signal.aborted) setState({ key, attempt, status: 'ready', result, updatedAt: Date.now() });
      } catch {
        if (!cancelled && (!controller.signal.aborted || timedOut)) setState({ key, attempt, status: 'error', result: null, updatedAt: null });
      } finally { window.clearTimeout(timeout); }
    }, 180);
    return () => { cancelled = true; window.clearTimeout(debounce); window.clearTimeout(timeout); controller.abort(); };
    // Only explicit choices affect ranking. Saves and other local UI state do not.
  }, [key, active, attempt]);
  // The same choices can be requested again. Hide the previous attempt before
  // the effect runs, so manual refresh never labels old results as refreshed.
  return { ...(state.key === key && state.attempt === attempt ? state
    : { key, attempt, status: 'loading' as const, result: null, updatedAt: null }),
    retry: () => setAttempt(value => value + 1) };
}
