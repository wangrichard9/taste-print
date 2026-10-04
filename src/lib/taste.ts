import { catalog, type Dish } from '../data/catalog';

export type Opinion = 'like' | 'pass';
export type TasteState = {
  version: 1;
  saved: string[];
  opinions: Record<string, Opinion>;
  onboarded: boolean;
};
export type BrowseFilter = 'all' | 'saved' | 'fresh' | 'comfort';

// Keep the sample-catalog profile intact under its old key; never transfer those
// opinions to different real recipes. This catalog starts a separate local profile.
export const storageKey = 'tasteprint:local:foodcom:v2';
export const emptyTaste = (): TasteState => ({ version: 1, saved: [], opinions: {}, onboarded: false });

export function parseTaste(raw: string | null): TasteState {
  if (!raw) return emptyTaste();
  const data: unknown = JSON.parse(raw);
  if (!data || typeof data !== 'object') throw new Error('Invalid local profile');
  const candidate = data as Record<string, unknown>;
  if (candidate.version !== 1 || !Array.isArray(candidate.saved) || typeof candidate.onboarded !== 'boolean'
    || !candidate.opinions || typeof candidate.opinions !== 'object' || Array.isArray(candidate.opinions)) {
    throw new Error('Unsupported local profile');
  }
  const ids = new Set(catalog.map(dish => dish.id));
  const opinions: Record<string, Opinion> = {};
  for (const [id, opinion] of Object.entries(candidate.opinions)) {
    if (ids.has(id) && (opinion === 'like' || opinion === 'pass')) opinions[id] = opinion;
  }
  return {
    version: 1, onboarded: candidate.onboarded,
    saved: [...new Set(candidate.saved.filter((id): id is string => typeof id === 'string' && ids.has(id)))],
    opinions,
  };
}

export function setOpinion(state: TasteState, id: string, opinion: Opinion): TasteState {
  if (!catalog.some(dish => dish.id === id)) return state;
  const opinions = { ...state.opinions };
  if (opinions[id] === opinion) delete opinions[id];
  else opinions[id] = opinion;
  return { ...state, opinions };
}

export function toggleSaved(state: TasteState, id: string): TasteState {
  if (!catalog.some(dish => dish.id === id)) return state;
  return { ...state, saved: state.saved.includes(id) ? state.saved.filter(saved => saved !== id) : [...state.saved, id] };
}

export function browseDishes(dishes: Dish[], query: string, filter: BrowseFilter, saved: string[]): Dish[] {
  const words = query.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
  return dishes.filter(dish => {
    const matchesFilter = filter === 'all' || (filter === 'saved' && saved.includes(dish.id))
      || (filter === 'fresh' && dish.tags.includes('Fresh')) || (filter === 'comfort' && dish.tags.includes('Comforting'));
    const text = [dish.name, dish.category, ...dish.tags, ...dish.ingredients].join(' ').toLocaleLowerCase();
    return matchesFilter && words.every(word => text.includes(word));
  });
}

// A descriptive count of explicit likes; NOT a trained model, prediction, or ranking.
export function describeTaste(opinions: Record<string, Opinion>) {
  const liked = catalog.filter(dish => opinions[dish.id] === 'like');
  const passed = catalog.filter(dish => opinions[dish.id] === 'pass');
  const counts = new Map<string, number>();
  for (const dish of liked) for (const tag of dish.tags) counts.set(tag, (counts.get(tag) ?? 0) + 1);
  const patterns = [...counts].map(([tag, count]) => ({ tag, count }))
    .sort((a, b) => b.count - a.count || a.tag.localeCompare(b.tag)).slice(0, 4);
  return { liked, passed, patterns };
}
