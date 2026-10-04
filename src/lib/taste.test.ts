import { describe, expect, it } from 'vitest';
import { catalog, reviewedCatalog } from '../data/catalog';
import { browseDishes, describeTaste, emptyTaste, parseTaste, setOpinion, toggleSaved, storageKey } from './taste';

describe('local taste data', () => {
  it('separates real recipe storage from the old sample catalog and rejects sample IDs', () => {
    expect(storageKey).not.toBe('tasteprint:local:v1');
    expect(parseTaste(JSON.stringify({ ...emptyTaste(), saved: ['gyoza'], opinions: { pizza: 'like' } })))
      .toEqual(emptyTaste());
  });
  it('starts empty and round-trips a saved profile', () => {
    expect(parseTaste(null)).toEqual(emptyTaste());
    const state = toggleSaved(setOpinion(emptyTaste(), 'foodcom:90975', 'like'), 'foodcom:60350');
    expect(parseTaste(JSON.stringify(state))).toEqual(state);
  });
  it('rejects corrupt JSON and unsupported schemas', () => {
    for (const raw of ['broken', 'null', '[]', '{"version":2}', JSON.stringify({ ...emptyTaste(), opinions: [] })]) {
      expect(() => parseTaste(raw)).toThrow();
    }
  });
  it('drops unknown dishes, invalid opinions, and duplicate saves', () => {
    expect(parseTaste(JSON.stringify({ ...emptyTaste(), saved: ['foodcom:60350', 'foodcom:60350', null, 'missing'],
      opinions: { 'foodcom:90975': 'like', 'foodcom:60350': 'maybe', missing: 'pass' } })))
      .toEqual({ ...emptyTaste(), saved: ['foodcom:60350'], opinions: { 'foodcom:90975': 'like' } });
  });
  it('toggles opinions without mutating history and allows switching', () => {
    const original = emptyTaste();
    const liked = setOpinion(original, 'foodcom:90975', 'like');
    expect(original.opinions).toEqual({});
    expect(setOpinion(liked, 'foodcom:90975', 'like').opinions).toEqual({});
    expect(setOpinion(liked, 'foodcom:90975', 'pass').opinions['foodcom:90975']).toBe('pass');
    expect(setOpinion(original, 'missing', 'like')).toBe(original);
  });
  it('saves independently of food preferences', () => {
    const state = toggleSaved(emptyTaste(), 'foodcom:60350');
    expect(state.opinions).toEqual({});
    expect(toggleSaved(state, 'foodcom:60350').saved).toEqual([]);
    expect(toggleSaved(state, 'missing')).toBe(state);
  });
});

describe('browsing and evidence', () => {
  it('searches ingredients, names and tags, combining filters and search terms', () => {
    expect(browseDishes(reviewedCatalog, ' BASIL ', 'all', []).map(dish => dish.id)).toEqual(['foodcom:28199', 'foodcom:95383', 'foodcom:131639', 'foodcom:47640', 'foodcom:749', 'foodcom:11808']);
    expect(browseDishes(catalog, 'fresh cucumber', 'fresh', []).map(dish => dish.id)).toEqual(['foodcom:90975', 'foodcom:322833']);
    expect(browseDishes(catalog, 'basil', 'saved', ['foodcom:28199']).map(dish => dish.id)).toEqual(['foodcom:28199']);
    expect(browseDishes(catalog, 'nonexistent', 'all', [])).toEqual([]);
  });
  it('keeps editorial order instead of pretending to personalize', () => {
    expect(browseDishes(catalog, '', 'all', [])).toEqual(catalog);
  });
  it('bases profile patterns only on explicitly liked dishes', () => {
    const summary = describeTaste({ 'foodcom:90975': 'like', 'foodcom:28199': 'like', 'foodcom:60350': 'pass', missing: 'like' });
    expect(summary.liked).toHaveLength(2);
    expect(summary.passed).toHaveLength(1);
    expect(summary.patterns.find(pattern => pattern.tag === 'Fresh')?.count).toBe(2);
    expect(summary.patterns.some(pattern => pattern.tag === 'Cheesy')).toBe(false);
    expect(describeTaste({}).patterns).toEqual([]);
  });
});
