import { ArrowUpRight } from 'lucide-react';
import { useState } from 'react';
import { dishById, formatRecipeTime, type Dish } from '../data/catalog';
import { recommendationReason } from '../lib/discovery';
import { ingredientGroups, type IngredientItem, type IngredientResult } from '../lib/ingredients';
import DishImage from './DishImage';

export function IngredientResultCard({ item, total, onOpenDish }: {
  item: IngredientItem; total: number; onOpenDish: (dish: Dish) => void;
}) {
  const dish = dishById.get(item.id)!;
  return <article className="fp-recipe ingredient-recipe">
    <button type="button" className="fp-recipe-image" onClick={() => onOpenDish(dish)} aria-label={`View ${dish.name}`}>
      <DishImage dish={dish} /><span>{item.knownLike ? 'Already liked' : 'New to your likes'}</span><ArrowUpRight size={18} aria-hidden="true" />
    </button>
    <div className="fp-recipe-meta"><span>{dish.category} · {formatRecipeTime(dish.totalMinutes)}</span></div>
    <h3><button type="button" onClick={() => onOpenDish(dish)}>{dish.name}</button></h3>
    <p className="ingredient-fit">{item.matchCount} / {total} ingredient names matched · {item.additionalIngredients.length} other listed ingredients</p>
    <p>{item.knownLike ? 'You already liked this recipe.' : recommendationReason({ ...item, basis: item.basis === 'co_like' ? 'co_like' : 'popularity' })}</p>
    <details className="ingredient-evidence"><summary>See ingredient matches and what else is listed</summary>
      <p>Matches: {item.matches.map(match => `${match.input} → ${match.recipeIngredient}`).join('; ')}.</p>
      <p>Also listed: {item.additionalIngredients.length ? item.additionalIngredients.join(', ') : 'No other ingredient names in this source list.'}</p>
    </details>
  </article>;
}

export default function IngredientResults({ result, onOpenDish }: { result: IngredientResult; onOpenDish: (dish: Dish) => void }) {
  const [newLimit, setNewLimit] = useState(12);
  const [knownLimit, setKnownLimit] = useState(6);
  const { newIdeas, knownFavorites } = ingredientGroups(result);
  return <>
    <div className="section-heading"><div><span className="eyebrow">YOUR LIST, WITH ROOM TO DISCOVER</span><h2>New ideas from here.</h2></div><span className="fp-sample-label">{result.newCount.toLocaleString()} matching new options</span></div>
    <p className="fp-results-context">Matching list: {result.ingredients.join(', ')}. Searched {result.catalogSize.toLocaleString()} model recipes; passed recipes are excluded.</p>
    <p className="evidence-note">Name matching uses simple rules, not substitutions. Additional ingredients are allowed. These source lists have no quantities and may be incomplete; check the original recipe before cooking. Not allergy guidance.</p>
    {!newIdeas.length && <p className="fp-body-copy">No new recipes matched this list. {knownFavorites.length ? 'Your matching favorites are below.' : 'Try a different ingredient or a more general ingredient name.'}</p>}
    <div className="fp-recipe-grid">{newIdeas.slice(0, newLimit).map(item => <IngredientResultCard key={item.id} item={item} total={result.ingredients.length} onOpenDish={onOpenDish} />)}</div>
    {newLimit < newIdeas.length && <button type="button" className="button secondary ingredient-more" onClick={() => setNewLimit(value => value + 12)}>Show more new options ({newIdeas.length - newLimit} remaining)</button>}
    {!!knownFavorites.length && <section className="ingredient-favorites"><div className="section-heading"><h2>Familiar, and still an option.</h2><span className="small-label">{knownFavorites.length} already liked</span></div><p className="fp-body-copy">Kept separate so familiar choices don’t crowd out new ideas.</p>
      <div className="fp-recipe-grid">{knownFavorites.slice(0, knownLimit).map(item => <IngredientResultCard key={item.id} item={item} total={result.ingredients.length} onOpenDish={onOpenDish} />)}</div>
      {knownLimit < knownFavorites.length && <button type="button" className="button secondary ingredient-more" onClick={() => setKnownLimit(value => value + 6)}>Show more favorites</button>}
    </section>}
  </>;
}
