import { describe, expect, it } from 'vitest';
import { catalog, reviewedCatalog } from '../data/catalog';
import { emptyTaste, parseTaste, setOpinion, toggleSaved } from './taste';
import { discoveryDishes, parseRecommendations, recipeChoices, recommendationReason, type RecommendationResult } from './discovery';

function response(): RecommendationResult {
  return { method: 'raw_co_like', mode: 'popularity', catalogSize: 5006, supportedLikeCount: 0,
    unsupportedLikeCount: 0, personalizedCount: 0, items: catalog.map(dish => ({ id: dish.id, basis: 'popularity' })) };
}

describe('local model discovery', () => {
  it('sends only explicit likes and passes, not saves or profile traits', () => {
    const taste = toggleSaved(setOpinion(emptyTaste(), reviewedCatalog[0].id, 'like'), reviewedCatalog[1].id);
    expect(recipeChoices(taste)).toEqual({ likes: [reviewedCatalog[0].id], passes: [] });
    expect(recipeChoices(setOpinion(taste, reviewedCatalog[0].id, 'pass'))).toEqual({ likes: [], passes: [reviewedCatalog[0].id] });
  });
  it('retains original and new recipe choices through persistence', () => {
    const extra = catalog[40];
    const taste = toggleSaved(setOpinion(setOpinion(emptyTaste(), reviewedCatalog[0].id, 'like'), extra.id, 'pass'), extra.id);
    expect(parseTaste(JSON.stringify(taste))).toEqual(taste);
    expect(parseTaste(JSON.stringify(taste)).opinions[extra.id]).toBe('pass');
  });
  it('accepts complete popularity fallback without pretending it is personal', () => {
    const result = parseRecommendations(response(), emptyTaste());
    expect(result.mode).toBe('popularity');
    expect(recommendationReason(result.items[0])).toContain('no shared-like evidence');
  });
  it('validates real evidence and prevents liked, passed, duplicate or unknown outputs', () => {
    const seed = reviewedCatalog[0].id;
    const taste = setOpinion(emptyTaste(), seed, 'like');
    const good = response();
    good.mode = 'co_like'; good.supportedLikeCount = 1; good.personalizedCount = 1;
    good.items = good.items.filter(item => item.id !== seed);
    good.items[0] = { ...good.items[0], basis: 'co_like', evidence: { seedId: seed, sharedLikers: 12 } };
    expect(parseRecommendations(good, taste).mode).toBe('co_like');
    expect(recommendationReason(good.items[0])).toContain('12 historical people');
    for (const mutate of [
      (value: RecommendationResult) => { value.items[1].id = seed; },
      (value: RecommendationResult) => { value.items[1].id = value.items[0].id; },
      (value: RecommendationResult) => { value.items[0].evidence!.sharedLikers = 0; },
      (value: RecommendationResult) => { value.items[0].evidence!.seedId = reviewedCatalog[2].id; },
      (value: RecommendationResult) => { value.catalogSize = 30; },
    ]) {
      const bad = structuredClone(good); mutate(bad);
      expect(() => parseRecommendations(bad, taste)).toThrow();
    }
  });
  it('preserves server rank through search and lets saved views contain seen dishes', () => {
    const result = response(); result.items.reverse();
    const taste = toggleSaved(setOpinion(emptyTaste(), reviewedCatalog[0].id, 'like'), reviewedCatalog[0].id);
    expect(discoveryDishes(result, emptyTaste(), '', 'all')[0].id).toBe(result.items[0].id);
    expect(discoveryDishes(null, taste, '', 'all').some(dish => dish.id === reviewedCatalog[0].id)).toBe(false);
    expect(discoveryDishes(null, taste, '', 'saved').map(dish => dish.id)).toEqual([reviewedCatalog[0].id]);
    expect(discoveryDishes(result, emptyTaste(), 'zzzz-no-match', 'all')).toEqual([]);
  });
});
