import { catalog, dishById, type Dish } from '../data/catalog';
import { browseDishes, type BrowseFilter, type TasteState } from './taste';

export type RecommendationItem = {
  id: string; basis: 'co_like' | 'popularity';
  evidence?: { seedId: string; sharedLikers: number };
};
export type RecommendationResult = {
  method: 'raw_co_like'; mode: 'co_like' | 'popularity'; catalogSize: number;
  supportedLikeCount: number; unsupportedLikeCount: number; personalizedCount: number;
  items: RecommendationItem[];
};

export function recipeChoices(taste: TasteState) {
  return { likes: Object.keys(taste.opinions).filter(id => taste.opinions[id] === 'like').sort(),
    passes: Object.keys(taste.opinions).filter(id => taste.opinions[id] === 'pass').sort() };
}

export function parseRecommendations(raw: unknown, taste: TasteState): RecommendationResult {
  if (!raw || typeof raw !== 'object') throw new Error('Invalid recommendation response');
  const result = raw as RecommendationResult;
  const choices = recipeChoices(taste);
  const seen = new Set([...choices.likes, ...choices.passes]);
  const supported = choices.likes.filter(id => dishById.get(id)?.modelSupported);
  const unseenCount = catalog.filter(dish => dish.modelSupported && !seen.has(dish.id)).length;
  if (result.method !== 'raw_co_like' || !['co_like', 'popularity'].includes(result.mode)
    || result.catalogSize !== catalog.filter(dish => dish.modelSupported).length
    || result.supportedLikeCount !== supported.length || result.unsupportedLikeCount !== choices.likes.length - supported.length
    || !Number.isInteger(result.personalizedCount) || result.personalizedCount < 0
    || !Array.isArray(result.items) || result.items.length !== unseenCount
    || result.personalizedCount > result.items.length
    || (result.mode === 'co_like') !== (result.personalizedCount > 0)) throw new Error('Invalid recommendation metadata');
  const ids = new Set<string>();
  let coCount = 0;
  let fallbackStarted = false;
  for (const item of result.items) {
    if (!item || !dishById.get(item.id)?.modelSupported || ids.has(item.id) || seen.has(item.id)
      || !['co_like', 'popularity'].includes(item.basis)) throw new Error('Invalid recommended recipe');
    ids.add(item.id);
    if (item.basis === 'co_like') {
      if (fallbackStarted || !item.evidence || !supported.includes(item.evidence.seedId)
        || !Number.isInteger(item.evidence.sharedLikers) || item.evidence.sharedLikers <= 0) throw new Error('Invalid recommendation evidence');
      coCount++;
    } else {
      fallbackStarted = true;
      if (item.evidence !== undefined) throw new Error('Popularity is not personalized evidence');
    }
  }
  if (coCount !== result.personalizedCount) throw new Error('Invalid evidence count');
  return result;
}

export function discoveryDishes(result: RecommendationResult | null, taste: TasteState, query: string, filter: BrowseFilter): Dish[] {
  const order = filter === 'saved' ? catalog : result ? result.items.map(item => dishById.get(item.id)!)
    : catalog.filter(dish => !taste.opinions[dish.id]);
  return browseDishes(order, query, filter, taste.saved);
}

export function recommendationReason(item: RecommendationItem): string {
  if (item.basis === 'popularity') return 'Popular choice · no shared-like evidence';
  const evidence = item.evidence!;
  return `${evidence.sharedLikers.toLocaleString()} historical ${evidence.sharedLikers === 1 ? 'person' : 'people'} liked this and ${dishById.get(evidence.seedId)!.name}.`;
}
