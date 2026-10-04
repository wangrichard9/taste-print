import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { catalog, reviewedCatalog } from '../data/catalog';
import { emptyTaste, setOpinion, type TasteState } from './taste';
import { discoveryDishes, recipeChoices, type RecommendationResult } from './discovery';
import { useRecommendations } from './useRecommendations';

// Hook-lifecycle harness, not a DOM substitute. Uses the real choice builder,
// response validation and All dishes ordering; browser checks are separate.
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

const seed = reviewedCatalog[0].id;
const liked = setOpinion(emptyTaste(), seed, 'like');
function response(taste = emptyTaste(), first = catalog[100].id) {
  const choices = recipeChoices(taste);
  const seen = new Set([...choices.likes, ...choices.passes]);
  const items: RecommendationResult['items'] = catalog.filter(dish => !seen.has(dish.id))
    .map(dish => ({ id: dish.id, basis: 'popularity' }));
  items.sort((a, b) => Number(b.id === first) - Number(a.id === first));
  if (choices.likes.length) items[0] = { ...items[0], basis: 'co_like', evidence: { seedId: choices.likes[0], sharedLikers: 12 } };
  return { ok: true, json: async (): Promise<RecommendationResult> => ({ method: 'raw_co_like',
    mode: choices.likes.length ? 'co_like' : 'popularity', catalogSize: catalog.length,
    supportedLikeCount: choices.likes.length, unsupportedLikeCount: 0,
    personalizedCount: choices.likes.length ? 1 : 0, items }) };
}
function render(taste: TasteState = emptyTaste(), active = true) {
  hooks.start(); return useRecommendations(taste, active);
}
beforeEach(() => { hooks.reset(); vi.useFakeTimers(); vi.stubGlobal('window', { setTimeout, clearTimeout }); });
afterEach(() => { hooks.unmount(); vi.useRealTimers(); vi.unstubAllGlobals(); });

describe('Discover recommendation lifecycle (hook harness)', () => {
  it('automatically sends a new like and uses the returned order in All dishes', async () => {
    const fetcher = vi.fn().mockResolvedValueOnce(response()).mockResolvedValueOnce(response(liked, catalog[101].id));
    vi.stubGlobal('fetch', fetcher);
    render(); await vi.advanceTimersByTimeAsync(180);
    expect(discoveryDishes(render().result, emptyTaste(), '', 'all')[0].id).toBe(catalog[100].id);
    expect(render(liked).result).toBeNull(); await vi.advanceTimersByTimeAsync(180);
    expect(JSON.parse(fetcher.mock.calls[1][1].body)).toEqual({ likes: [seed], passes: [] });
    const result = render(liked).result;
    expect(result?.supportedLikeCount).toBe(1);
    expect(discoveryDishes(result, liked, '', 'all')[0].id).toBe(catalog[101].id);
    expect(discoveryDishes(result, liked, '', 'all').some(dish => dish.id === seed)).toBe(false);
  });
  it('reranks passes, but does not treat saves as likes', async () => {
    const fetcher = vi.fn().mockResolvedValue(response()); vi.stubGlobal('fetch', fetcher);
    render(); await vi.advanceTimersByTimeAsync(180);
    render({ ...emptyTaste(), saved: [seed] }); await vi.advanceTimersByTimeAsync(180);
    expect(fetcher).toHaveBeenCalledTimes(1);
    const passed = setOpinion(emptyTaste(), seed, 'pass');
    fetcher.mockResolvedValue(response(passed)); render(passed); await vi.advanceTimersByTimeAsync(180);
    expect(JSON.parse(fetcher.mock.calls[1][1].body).passes).toEqual([seed]);
    expect(render(passed).result?.items.some(item => item.id === seed)).toBe(false);
  });
  it('requests the latest choices on returning to Discover', async () => {
    const fetcher = vi.fn().mockResolvedValue(response(liked)); vi.stubGlobal('fetch', fetcher);
    render(emptyTaste(), false); render(liked, false); await vi.advanceTimersByTimeAsync(180);
    expect(fetcher).not.toHaveBeenCalled();
    render(liked); await vi.advanceTimersByTimeAsync(180);
    expect(JSON.parse(fetcher.mock.calls[0][1].body).likes).toEqual([seed]);
    expect(render(liked).status).toBe('ready');
  });
  it('manual refresh immediately hides the prior result even for the same choices', async () => {
    const fetcher = vi.fn().mockResolvedValue(response(liked)); vi.stubGlobal('fetch', fetcher);
    render(liked); await vi.advanceTimersByTimeAsync(180);
    const ready = render(liked); expect(ready.status).toBe('ready');
    expect(ready.updatedAt).toBeTypeOf('number');
    ready.retry();
    const refreshing = render(liked);
    expect(refreshing.status).toBe('loading'); expect(refreshing.result).toBeNull();
    expect(refreshing.updatedAt).toBeNull();
    await vi.advanceTimersByTimeAsync(180);
    expect(fetcher).toHaveBeenCalledTimes(2);
    expect(fetcher.mock.calls[1][1].body).toBe(fetcher.mock.calls[0][1].body);
    expect(render(liked).status).toBe('ready');
    expect(render(liked).updatedAt).toBeGreaterThan(ready.updatedAt!);
  });
  it('ignores a replaced request that resolves after the new ranking', async () => {
    let finish!: (value: ReturnType<typeof response>) => void;
    const fetcher = vi.fn().mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }))
      .mockResolvedValueOnce(response(liked)); vi.stubGlobal('fetch', fetcher);
    render(); await vi.advanceTimersByTimeAsync(180);
    render(liked); await vi.advanceTimersByTimeAsync(180);
    finish(response()); await vi.advanceTimersByTimeAsync(0);
    expect(fetcher.mock.calls[0][1].signal.aborted).toBe(true);
    expect(render(liked).result?.supportedLikeCount).toBe(1);
  });
  it('shows failures instead of old results and supports retry', async () => {
    const fetcher = vi.fn().mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce(response(liked));
    vi.stubGlobal('fetch', fetcher); render(liked); await vi.advanceTimersByTimeAsync(180);
    const failed = render(liked); expect(failed.status).toBe('error'); expect(failed.result).toBeNull();
    failed.retry(); render(liked); await vi.advanceTimersByTimeAsync(180);
    expect(render(liked).status).toBe('ready');
  });
});
