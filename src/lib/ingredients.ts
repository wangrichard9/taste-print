import { catalog, dishById } from '../data/catalog';
import { recipeChoices, type RecommendationItem } from './discovery';
import type { TasteState } from './taste';

export type IngredientPriority = 'balanced' | 'ingredients' | 'taste';
export type IngredientRequest = { ingredients: string[]; priority: IngredientPriority };
export type IngredientItem = {
  id: string; knownLike: boolean; basis: 'known_like' | RecommendationItem['basis'];
  evidence?: RecommendationItem['evidence']; matchedInputs: string[]; matchCount: number;
  matches: { input: string; recipeIngredient: string }[]; additionalIngredients: string[];
};
export type IngredientResult = {
  method: 'ingredient_rules+raw_co_like'; priority: IngredientPriority; ingredients: string[];
  catalogSize: number; supportedLikeCount: number; newCount: number; knownCount: number; items: IngredientItem[];
};

export function addIngredientNames(current: string[], draft: string): string[] {
  const next = [...current];
  for (const part of draft.split(',')) {
    const label = part.trim().replace(/\s+/g, ' ');
    if (!label) continue;
    if (label.length > 40 || !/\p{L}/u.test(label)) throw new Error('Use ingredient names with letters, up to 40 characters each.');
    if (!next.some(item => item.toLocaleLowerCase() === label.toLocaleLowerCase())) next.push(label);
  }
  if (next.length > 12) throw new Error('Keep this first list to 12 ingredients.');
  return next;
}

const textList = (value: unknown): value is string[] => Array.isArray(value)
  && value.every(item => typeof item === 'string' && item.length > 0) && new Set(value).size === value.length;

export function parseIngredientResult(raw: unknown, request: IngredientRequest, taste: TasteState): IngredientResult {
  if (!raw || typeof raw !== 'object') throw new Error('Invalid ingredient response');
  const result = raw as IngredientResult;
  const choices = recipeChoices(taste);
  const supported = choices.likes.filter(id => dishById.get(id)?.modelSupported);
  if (result.method !== 'ingredient_rules+raw_co_like' || result.priority !== request.priority
    || !textList(result.ingredients) || !result.ingredients.length
    || !result.ingredients.every(label => request.ingredients.includes(label))
    || result.catalogSize !== catalog.filter(dish => dish.modelSupported).length
    || result.supportedLikeCount !== supported.length || !Array.isArray(result.items)
    || !Number.isInteger(result.newCount) || result.newCount < 0
    || !Number.isInteger(result.knownCount) || result.knownCount < 0
    || result.newCount + result.knownCount !== result.items.length) throw new Error('Invalid ingredient metadata');
  const ids = new Set<string>();
  let knownCount = 0;
  for (const item of result.items) {
    const dish = item && dishById.get(item.id);
    if (!dish?.modelSupported || ids.has(item.id) || choices.passes.includes(item.id)
      || typeof item.knownLike !== 'boolean' || item.knownLike !== choices.likes.includes(item.id)
      || !['known_like', 'co_like', 'popularity'].includes(item.basis)
      || (item.basis === 'known_like') !== item.knownLike
      || !textList(item.matchedInputs) || !item.matchedInputs.length
      || !item.matchedInputs.every(label => result.ingredients.includes(label))
      || !Number.isInteger(item.matchCount) || item.matchCount <= 0 || item.matchCount > item.matchedInputs.length
      || !textList(item.additionalIngredients) || !item.additionalIngredients.every(label => dish.ingredients.includes(label))
      || !Array.isArray(item.matches) || !item.matches.length) throw new Error('Invalid ingredient match');
    const pairs = new Set<string>();
    for (const match of item.matches) {
      if (!match || !item.matchedInputs.includes(match.input) || !dish.ingredients.includes(match.recipeIngredient)
        || item.additionalIngredients.includes(match.recipeIngredient)
        || pairs.has(JSON.stringify(match))) throw new Error('Invalid source ingredient evidence');
      pairs.add(JSON.stringify(match));
    }
    if (item.matchCount > new Set(item.matches.map(match => match.recipeIngredient)).size
      || !item.matchedInputs.every(label => item.matches.some(match => match.input === label))) throw new Error('Invalid coverage');
    if (item.basis === 'co_like') {
      if (!item.evidence || !supported.includes(item.evidence.seedId)
        || !Number.isInteger(item.evidence.sharedLikers) || item.evidence.sharedLikers <= 0) throw new Error('Invalid taste evidence');
    } else if (item.evidence !== undefined) throw new Error('Unexpected taste evidence');
    ids.add(item.id);
    if (item.knownLike) knownCount++;
  }
  if (knownCount !== result.knownCount) throw new Error('Invalid favorite count');
  return result;
}

export function ingredientGroups(result: IngredientResult) {
  return { newIdeas: result.items.filter(item => !item.knownLike), knownFavorites: result.items.filter(item => item.knownLike) };
}
