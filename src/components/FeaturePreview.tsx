import { ArrowUpRight, Bookmark, Sparkles } from 'lucide-react';
import type { ReactNode } from 'react';
import { formatRecipeTime, type Dish } from '../data/catalog';
import DishImage from './DishImage';

export function PreviewNotice({ children }: { children: ReactNode }) {
  return <div className="fp-notice"><Sparkles size={16} aria-hidden="true" /><p><strong>Design preview</strong><span>{children}</span></p></div>;
}

export function RecipePreviewCard({ dish, onOpen, note, onUnsave }: {
  dish: Dish; onOpen: () => void; note?: string; onUnsave?: () => void;
}) {
  return <article className="fp-recipe">
    <button type="button" className="fp-recipe-image" onClick={onOpen} aria-label={`View ${dish.name}`}><DishImage dish={dish} />
      <span>{dish.tags[0]}</span><ArrowUpRight size={18} aria-hidden="true" /></button>
    <div className="fp-recipe-meta"><span>{dish.category} · {formatRecipeTime(dish.totalMinutes)}</span>{onUnsave && <button type="button" onClick={onUnsave} aria-label={`Unsave ${dish.name}`}><Bookmark size={15} fill="currentColor" aria-hidden="true" /> Saved</button>}</div>
    <h3><button type="button" onClick={onOpen}>{dish.name}</button></h3>
    <p>{note ?? dish.description}</p>
  </article>;
}
