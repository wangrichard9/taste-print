import { describe, expect, it } from 'vitest';
import { reviewedCatalog, catalog } from '../data/catalog';
import { addIngredientNames, ingredientGroups, parseIngredientResult, type IngredientRequest, type IngredientResult } from './ingredients';
import { emptyTaste as createEmptyTaste } from './taste';

const emptyTaste = createEmptyTaste();

const dish = reviewedCatalog[0];
const request: IngredientRequest = { ingredients: [dish.ingredients[0]], priority: 'balanced' };
export function resultFixture(): IngredientResult {
  return { method: 'ingredient_rules+raw_co_like', priority: 'balanced', ingredients: request.ingredients,
    catalogSize: catalog.length, supportedLikeCount: 0, newCount: 1, knownCount: 0,
    items: [{ id: dish.id, basis: 'popularity', knownLike: false, matchCount: 1, matchedInputs: request.ingredients,
      matches: [{ input: request.ingredients[0], recipeIngredient: dish.ingredients[0] }], additionalIngredients: [] }] };
}

describe('ingredient inputs and response contract', () => {
  it('combines pending draft and chips without mutating or duplicating names', () => {
    const current = ['Tomatoes'];
    expect(addIngredientNames(current, ' tomatoes,  Spinach , ')).toEqual(['Tomatoes', 'Spinach']);
    expect(current).toEqual(['Tomatoes']);
    expect(addIngredientNames([], 'rice, chickpeas')).toEqual(['rice', 'chickpeas']);
  });
  it('rejects limits and non-names without partially adding a draft', () => {
    expect(() => addIngredientNames([], 'a'.repeat(41))).toThrow();
    expect(() => addIngredientNames([], 'rice,123')).toThrow();
    expect(() => addIngredientNames(Array.from({ length: 12 }, (_, i) => `name${i}`), 'spinach')).toThrow();
  });
  it('accepts real source evidence and a genuine empty result', () => {
    expect(parseIngredientResult(resultFixture(), request, emptyTaste)).toEqual(resultFixture());
    const none = { ...resultFixture(), newCount: 0, items: [] };
    expect(parseIngredientResult(none, request, emptyTaste).items).toEqual([]);
  });
  it('rejects mismatched priority, metadata, passed recipes, and invented ingredient evidence', () => {
    const bad = [ { ...resultFixture(), priority: 'taste' }, { ...resultFixture(), newCount: 2 },
      { ...resultFixture(), ingredients: ['invented'] }, { ...resultFixture(), catalogSize: 1 } ];
    for (const raw of bad) expect(() => parseIngredientResult(raw, request, emptyTaste)).toThrow();
    expect(() => parseIngredientResult(resultFixture(), request, { ...emptyTaste, opinions: { [dish.id]: 'pass' } })).toThrow();
    const raw = resultFixture(); raw.items[0].matches[0].recipeIngredient = 'invented ingredient';
    expect(() => parseIngredientResult(raw, request, emptyTaste)).toThrow();
  });
  it('distinguishes explicit favorites from shared-like evidence and popularity', () => {
    const liked = { ...emptyTaste, opinions: { [dish.id]: 'like' as const } };
    const raw = resultFixture(); raw.supportedLikeCount = 1; raw.newCount = 0; raw.knownCount = 1;
    raw.items[0].knownLike = true; raw.items[0].basis = 'known_like';
    expect(ingredientGroups(parseIngredientResult(raw, request, liked)).knownFavorites).toHaveLength(1);
    raw.items[0].evidence = { seedId: dish.id, sharedLikers: 1 };
    expect(() => parseIngredientResult(raw, request, liked)).toThrow();
  });
  it('validates shared-liker evidence and does not treat saving as a taste signal', () => {
    const other = reviewedCatalog[1];
    const taste = { ...emptyTaste, opinions: { [other.id]: 'like' as const }, saved: [dish.id] };
    const raw = resultFixture(); raw.supportedLikeCount = 1; raw.items[0].basis = 'co_like';
    raw.items[0].evidence = { seedId: other.id, sharedLikers: 2 };
    expect(parseIngredientResult(raw, request, taste).newCount).toBe(1);
    raw.items[0].evidence.sharedLikers = 0;
    expect(() => parseIngredientResult(raw, request, taste)).toThrow();
  });
  it('rejects duplicate results, overlap with extra ingredients, and impossible coverage', () => {
    const raw = resultFixture(); raw.newCount = 2; raw.items.push({ ...raw.items[0] });
    expect(() => parseIngredientResult(raw, request, emptyTaste)).toThrow();
    const overlap = resultFixture(); overlap.items[0].additionalIngredients = [dish.ingredients[0]];
    expect(() => parseIngredientResult(overlap, request, emptyTaste)).toThrow();
    const inflated = resultFixture(); inflated.items[0].matchCount = 2;
    expect(() => parseIngredientResult(inflated, request, emptyTaste)).toThrow();
  });
});
