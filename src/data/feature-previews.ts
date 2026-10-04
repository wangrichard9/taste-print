import { catalog } from './catalog';
import type { Opinion, TasteState } from '../lib/taste';

// Authored design fixtures. Never use these as recommendation outputs or save them
// into the visitor's profile. Recipe metadata still comes from the real catalog.
function recipes(ids: number[]) {
  return ids.map(id => {
    const dish = catalog.find(recipe => recipe.sourceRecipeId === id);
    if (!dish) throw new Error(`Missing preview recipe ${id}`);
    return dish;
  });
}

export const previewRecipes = {
  ingredients: recipes([81968, 25360, 131639]),
  group: recipes([91318, 11808, 266209]),
  explore: recipes([95383, 115954]),
};

export const exampleTaste: TasteState = {
  version: 1,
  onboarded: true,
  saved: recipes([81968, 11808, 131639]).map(dish => dish.id),
  opinions: Object.fromEntries([
    ...recipes([90975, 28199, 91318, 95383]).map(dish => [dish.id, 'like' as Opinion]),
    ...recipes([29301, 60350]).map(dish => [dish.id, 'pass' as Opinion]),
  ]),
};

export const samplePeople = [
  { id: 'alex', name: 'Alex', initial: 'A', subtitle: 'Bright flavours, fresh starts.', tags: ['Fresh', 'Tangy', 'Herby'] },
  { id: 'maya', name: 'Maya', initial: 'M', subtitle: 'Something warm and comforting.', tags: ['Comforting', 'Savory', 'Creamy'] },
  { id: 'jordan', name: 'Jordan', initial: 'J', subtitle: 'A little spice goes a long way.', tags: ['Spiced', 'Herby', 'Savory'] },
  { id: 'sam', name: 'Sam', initial: 'S', subtitle: 'Vegetables at the centre.', tags: ['Vegetable-forward', 'Fresh', 'Savory'] },
] as const;

// These words illustrate how a future group explanation could look. They are
// fixed editorial examples, not calculated satisfaction or safety judgments.
export const groupNotes: Record<string, Record<string, string>> = {
  'foodcom:91318': { alex: 'Fresh & bright', maya: 'Something to try', jordan: 'Savory notes', sam: 'Something to try' },
  'foodcom:11808': { alex: 'Herby notes', maya: 'Comforting', jordan: 'Savory notes', sam: 'Something to try' },
  'foodcom:266209': { alex: 'Herby notes', maya: 'Something to try', jordan: 'Spiced & savory', sam: 'A different direction' },
};
