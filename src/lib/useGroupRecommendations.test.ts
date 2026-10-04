import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { reviewedCatalog } from '../data/catalog';
import { groupRequest, newGuest, type GroupRequest } from './mealmerge';
import { emptyTaste } from './taste';
import { groupFixture } from '../test/groupFixture';
import { useGroupRecommendations } from './useGroupRecommendations';

const hooks = vi.hoisted(() => {
  let values: unknown[] = [], cursor = 0, deps: unknown[] | undefined, cleanup: (() => void) | undefined;
  return { start: () => { cursor = 0; }, reset: () => { cleanup?.(); values = []; cursor = 0; deps = undefined; cleanup = undefined; },
    unmount: () => { cleanup?.(); cleanup = undefined; },
    useState: <T,>(initial: T): [T, (next: T | ((value: T) => T)) => void] => {
      const slot = cursor++; if (values.length <= slot) values[slot] = initial;
      return [values[slot] as T, next => { values[slot] = typeof next === 'function' ? (next as (value: T) => T)(values[slot] as T) : next; }];
    },
    useEffect: (effect: () => (() => void) | void, next: unknown[]) => {
      if (!deps || next.some((value, i) => value !== deps![i])) { cleanup?.(); deps = next; cleanup = effect() || undefined; }
    },
  };
});
vi.mock('react', () => ({ useState: hooks.useState, useEffect: hooks.useEffect }));
const request = groupRequest(emptyTaste(), [newGuest()], 'balanced');
const response = (input = request) => ({ ok: true, json: async () => groupFixture(input) });
function render(input: GroupRequest | null = request) { hooks.start(); return useGroupRecommendations(input); }
beforeEach(() => { hooks.reset(); vi.useFakeTimers(); vi.stubGlobal('window', { setTimeout, clearTimeout }); });
afterEach(() => { hooks.unmount(); vi.useRealTimers(); vi.unstubAllGlobals(); });

describe('MealMerge request lifecycle (hook harness, not browser)', () => {
  it('does not request before submission and posts all member choices after submission', async () => {
    const fetcher = vi.fn().mockResolvedValue(response()); vi.stubGlobal('fetch', fetcher);
    expect(render(null).status).toBe('idle'); expect(fetcher).not.toHaveBeenCalled();
    expect(render().status).toBe('loading'); await vi.advanceTimersByTimeAsync(180);
    expect(JSON.parse(fetcher.mock.calls[0][1].body)).toEqual(request); expect(render().status).toBe('ready');
  });
  it('aborts a replaced mode and ignores its late response', async () => {
    let first!: (value: ReturnType<typeof response>) => void;
    const next = { ...request, priority: 'overall' as const };
    const fetcher = vi.fn().mockImplementationOnce(() => new Promise(resolve => { first = resolve; })).mockResolvedValueOnce(response(next));
    vi.stubGlobal('fetch', fetcher); render(); await vi.advanceTimersByTimeAsync(180);
    expect(render(next).result).toBeNull(); await vi.advanceTimersByTimeAsync(180);
    first(response()); await vi.advanceTimersByTimeAsync(0);
    expect(fetcher.mock.calls[0][1].signal.aborted).toBe(true); expect(render(next).result?.priority).toBe('overall');
  });
  it('clears obsolete results when editing the table, including resubmission of the same content', async () => {
    const fetcher = vi.fn().mockResolvedValue(response()); vi.stubGlobal('fetch', fetcher);
    render(); await vi.advanceTimersByTimeAsync(180); expect(render().status).toBe('ready');
    expect(render(null).result).toBeNull(); expect(render().status).toBe('loading');
    await vi.advanceTimersByTimeAsync(180); hooks.unmount(); expect(fetcher.mock.calls[1][1].signal.aborted).toBe(true);
  });
  it('retries service failures and distinguishes rejected profiles from a missing service', async () => {
    const fetcher = vi.fn().mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce({ ok: false, status: 400 }).mockResolvedValueOnce(response());
    vi.stubGlobal('fetch', fetcher); render(); await vi.advanceTimersByTimeAsync(180);
    let state = render(); expect(state.status).toBe('error'); state.retry(); render(); await vi.advanceTimersByTimeAsync(180);
    state = render(); expect(state.status).toBe('invalid'); state.retry(); render(); await vi.advanceTimersByTimeAsync(180);
    expect(render().status).toBe('ready');
  });
  it('times out and aborts a hung service request', async () => {
    const fetcher = vi.fn().mockImplementation((_url, options) => new Promise((_resolve, reject) => options.signal.addEventListener('abort', () => reject(new Error('aborted')))));
    vi.stubGlobal('fetch', fetcher); render(); await vi.advanceTimersByTimeAsync(10000);
    expect(render().status).toBe('error'); expect(fetcher.mock.calls[0][1].signal.aborted).toBe(true);
  });
  it('reranks for profile changes but not a personal save', async () => {
    const fetcher = vi.fn().mockImplementation(() => new Promise(() => {})); vi.stubGlobal('fetch', fetcher);
    render(); await vi.advanceTimersByTimeAsync(180);
    render(groupRequest({ ...emptyTaste(), saved: [reviewedCatalog[0].id] }, [newGuest()], 'balanced'));
    await vi.advanceTimersByTimeAsync(180); expect(fetcher).toHaveBeenCalledTimes(1);
    render(groupRequest({ ...emptyTaste(), opinions: { [reviewedCatalog[0].id]: 'like' } }, [newGuest()], 'balanced'));
    await vi.advanceTimersByTimeAsync(180); expect(fetcher).toHaveBeenCalledTimes(2);
  });
});
