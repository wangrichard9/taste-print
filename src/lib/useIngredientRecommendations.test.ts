import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { catalog, reviewedCatalog } from '../data/catalog';
import { emptyTaste } from './taste';
import { useIngredientRecommendations } from './useIngredientRecommendations';
import type { IngredientRequest } from './ingredients';

// Minimal hook-lifecycle harness. Tests request cleanup/state guards, not DOM or
// React rendering; interactive browser checks remain a separate verification.
const hooks = vi.hoisted(() => {
  let values: unknown[] = [], cursor = 0;
  let deps: unknown[] | undefined, cleanup: (() => void) | undefined;
  return {
    start: () => { cursor = 0; },
    reset: () => { cleanup?.(); values = []; cursor = 0; deps = undefined; cleanup = undefined; },
    unmount: () => { cleanup?.(); cleanup = undefined; },
    useState: <T,>(initial: T): [T, (next: T | ((value: T) => T)) => void] => {
      const slot = cursor++;
      if (values.length <= slot) values[slot] = initial;
      return [values[slot] as T, next => { values[slot] = typeof next === 'function' ? (next as (value: T) => T)(values[slot] as T) : next; }];
    },
    useEffect: (effect: () => (() => void) | void, next: unknown[]) => {
      if (!deps || next.some((value, i) => value !== deps![i])) { cleanup?.(); deps = next; cleanup = effect() || undefined; }
    },
  };
});
vi.mock('react', () => ({ useState: hooks.useState, useEffect: hooks.useEffect }));

const dish = reviewedCatalog[0];
const request: IngredientRequest = { ingredients: [dish.ingredients[0]], priority: 'balanced' };
function response(priority = 'balanced') {
  return { ok: true, json: async () => ({ method: 'ingredient_rules+raw_co_like', priority,
    ingredients: request.ingredients, catalogSize: catalog.length, supportedLikeCount: 0,
    newCount: 1, knownCount: 0, items: [{ id: dish.id, knownLike: false, basis: 'popularity', matchCount: 1,
      matchedInputs: request.ingredients, matches: [{ input: dish.ingredients[0], recipeIngredient: dish.ingredients[0] }], additionalIngredients: [] }] }) };
}
function render(input: IngredientRequest | null = request, taste = emptyTaste()) {
  hooks.start(); return useIngredientRecommendations(input, taste);
}
beforeEach(() => { hooks.reset(); vi.useFakeTimers(); vi.stubGlobal('window', { setTimeout, clearTimeout }); });
afterEach(() => { hooks.unmount(); vi.useRealTimers(); vi.unstubAllGlobals(); });

describe('ingredient request lifecycle (hook harness, not browser)', () => {
  it('does not fetch before submission; fetches the complete submitted list', async () => {
    const fetcher = vi.fn().mockResolvedValue(response()); vi.stubGlobal('fetch', fetcher);
    expect(render(null).status).toBe('idle'); expect(fetcher).not.toHaveBeenCalled();
    expect(render().status).toBe('loading'); await vi.advanceTimersByTimeAsync(180);
    expect(JSON.parse(fetcher.mock.calls[0][1].body).ingredients).toEqual(request.ingredients);
    expect(render().status).toBe('ready');
  });
  it('aborts a replaced request and ignores its late response', async () => {
    let resolveFirst!: (value: ReturnType<typeof response>) => void;
    const fetcher = vi.fn().mockImplementationOnce(() => new Promise(resolve => { resolveFirst = resolve; }))
      .mockResolvedValueOnce(response('taste'));
    vi.stubGlobal('fetch', fetcher); render(); await vi.advanceTimersByTimeAsync(180);
    const next: IngredientRequest = { ...request, priority: 'taste' };
    expect(render(next).result).toBeNull(); await vi.advanceTimersByTimeAsync(180);
    resolveFirst(response()); await vi.advanceTimersByTimeAsync(0);
    expect(fetcher.mock.calls[0][1].signal.aborted).toBe(true);
    expect(render(next).result?.priority).toBe('taste');
  });
  it('clears visible results and aborts when the list is edited or page is closed', async () => {
    const fetcher = vi.fn().mockResolvedValue(response()); vi.stubGlobal('fetch', fetcher);
    render(); await vi.advanceTimersByTimeAsync(180); expect(render().status).toBe('ready');
    expect(render(null).result).toBeNull(); expect(fetcher.mock.calls[0][1].signal.aborted).toBe(true);
    expect(render().status).toBe('loading'); await vi.advanceTimersByTimeAsync(180); hooks.unmount();
    expect(fetcher.mock.calls[1][1].signal.aborted).toBe(true);
  });
  it('shows service failures and supports a retry instead of sample results', async () => {
    const fetcher = vi.fn().mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce(response());
    vi.stubGlobal('fetch', fetcher); render(); await vi.advanceTimersByTimeAsync(180);
    const failed = render(); expect(failed.status).toBe('error'); expect(failed.result).toBeNull();
    failed.retry(); render(); await vi.advanceTimersByTimeAsync(180); expect(render().status).toBe('ready');
  });
  it('reports a timed-out request and aborts it', async () => {
    const fetcher = vi.fn().mockImplementation((_url, options) => new Promise((_resolve, reject) => {
      options.signal.addEventListener('abort', () => reject(new Error('aborted')));
    }));
    vi.stubGlobal('fetch', fetcher); render(); await vi.advanceTimersByTimeAsync(10000);
    expect(render().status).toBe('error'); expect(fetcher.mock.calls[0][1].signal.aborted).toBe(true);
  });
  it('distinguishes an invalid list from a disconnected service', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: false, status: 400 }));
    render(); await vi.advanceTimersByTimeAsync(180);
    expect(render().status).toBe('invalid'); expect(render().result).toBeNull();
  });
  it('reranks for explicit choices, but not saves', async () => {
    const fetcher = vi.fn().mockImplementation(() => new Promise(() => {})); vi.stubGlobal('fetch', fetcher);
    render(); await vi.advanceTimersByTimeAsync(180);
    render(request, { ...emptyTaste(), saved: [dish.id] }); await vi.advanceTimersByTimeAsync(180);
    expect(fetcher).toHaveBeenCalledTimes(1);
    render(request, { ...emptyTaste(), opinions: { [dish.id]: 'like' } }); await vi.advanceTimersByTimeAsync(180);
    expect(fetcher).toHaveBeenCalledTimes(2);
    expect(JSON.parse(fetcher.mock.calls[1][1].body).likes).toEqual([dish.id]);
  });
});
