import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { guestStorageKey, newGuest } from './mealmerge';
import { storageKey } from './taste';
import { useMealMergeGuests } from './useMealMergeGuests';

const hooks = vi.hoisted(() => {
  let values: unknown[] = [], cursor = 0;
  return { reset: () => { values = []; cursor = 0; }, start: () => { cursor = 0; },
    useState: <T,>(initial: T | (() => T)): [T, (next: T | ((value: T) => T)) => void] => {
      const slot = cursor++; if (values.length <= slot) values[slot] = typeof initial === 'function' ? (initial as () => T)() : initial;
      return [values[slot] as T, next => { values[slot] = typeof next === 'function' ? (next as (value: T) => T)(values[slot] as T) : next; }];
    }, useEffect: (effect: () => void) => effect(),
  };
});
vi.mock('react', () => ({ useState: hooks.useState, useEffect: hooks.useEffect }));
function render() { hooks.start(); return useMealMergeGuests(); }
beforeEach(() => hooks.reset()); afterEach(() => vi.unstubAllGlobals());
describe('guest storage isolation (hook harness)', () => {
  it('reads/writes only the guest key and preserves the personal record', () => {
    const records = new Map([[storageKey, 'personal sentinel'], [guestStorageKey, JSON.stringify({ version: 1, guests: [{ ...newGuest(), name: 'Maya' }] })]]);
    const getItem = vi.fn((key: string) => records.get(key) ?? null), setItem = vi.fn((key: string, value: string) => records.set(key, value));
    vi.stubGlobal('localStorage', { getItem, setItem });
    const state = render(); expect(state.guests[0].name).toBe('Maya'); state.setGuests([{ ...newGuest(), name: '' }]); render();
    expect(getItem).toHaveBeenCalledWith(guestStorageKey); expect(setItem.mock.calls.every(([key]) => key === guestStorageKey)).toBe(true);
    expect(records.get(storageKey)).toBe('personal sentinel'); expect(JSON.parse(records.get(guestStorageKey)!).guests[0].name).toBe('Guest 1');
  });
  it('labels a corrupt guest record without taking personal choices as guest defaults', () => {
    vi.stubGlobal('localStorage', { getItem: () => 'broken json', setItem: () => {} });
    const state = render(); expect(state.warning).toContain('your Tasteprint is unchanged'); expect(state.guests[0].opinions).toEqual({});
  });
  it('keeps editing usable and warns when browser storage fails', () => {
    vi.stubGlobal('localStorage', { getItem: () => null, setItem: () => { throw new Error('blocked'); } });
    render(); expect(render().warning).toContain('may not survive a refresh');
  });
});
