import { expect, it } from 'vitest';
import { reviewedCatalog } from '../data/catalog';
import { emptyTaste } from './taste';
import { parseIngredientResult, type IngredientPriority } from './ingredients';

// Opt-in end-to-end API/decoder contract; does not claim interactive UI QA.
it.skipIf(import.meta.env.VITE_TASTEPRINT_LIVE_TEST !== '1')('decodes real ingredient results through the running Vite proxy', async () => {
  const taste = emptyTaste();
  for (const dish of reviewedCatalog.slice(0, 6)) taste.opinions[dish.id] = 'like';
  taste.opinions[reviewedCatalog[6].id] = 'pass';
  const firstIds: string[] = [];
  for (const priority of ['balanced', 'ingredients', 'taste'] as IngredientPriority[]) {
    const request = { ingredients: ['Tomatoes', 'Spinach', 'Chickpeas'], priority };
    const response = await fetch('http://127.0.0.1:5173/api/ingredients', { method: 'POST',
      headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...request,
        likes: reviewedCatalog.slice(0, 6).map(dish => dish.id), passes: [reviewedCatalog[6].id] }), signal: AbortSignal.timeout(10000) });
    expect(response.ok).toBe(true);
    const result = parseIngredientResult(await response.json(), request, taste);
    expect(result.newCount).toBeGreaterThan(3); expect(result.knownCount).toBeGreaterThan(0);
    firstIds.push(result.items.find(item => !item.knownLike)!.id);
  }
  expect(new Set(firstIds).size).toBeGreaterThan(1);
}, 30000);
