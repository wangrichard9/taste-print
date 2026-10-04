import { useState } from 'react';
import { ArrowUpRight, Search } from 'lucide-react';
import { catalog, reviewedCatalog, formatRecipeTime } from '../data/catalog';
import { browseDishes, type Opinion } from '../lib/taste';
import type { Guest } from '../lib/mealmerge';
import DishImage from './DishImage';
import { OpinionButtons } from './Onboarding';

export default function GuestEditor({ guest, onRename, onPick, onClear, onDone }: {
  guest: Guest; onRename: (name: string) => void; onPick: (id: string, opinion: Opinion) => void;
  onClear: () => void; onDone: () => void;
}) {
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState<'reviewed' | 'all' | 'choices'>('reviewed');
  const [limit, setLimit] = useState(12);
  const name = guest.name.trim() || `Guest ${guest.id.slice(-1)}`;
  const base = filter === 'reviewed' ? reviewedCatalog : filter === 'choices' ? catalog.filter(dish => guest.opinions[dish.id]) : catalog;
  const dishes = browseDishes(base, query, 'all', []);
  return <section className="mm-guest-editor" aria-labelledby="guest-editor-title">
    <div className="section-heading"><div><span className="eyebrow">ONLY THIS GUEST’S CHOICES</span><h2 id="guest-editor-title">Editing {name}.</h2></div><button type="button" className="button secondary" onClick={onDone}>Done editing</button></div>
    <label className="mm-name-label">Guest name<input value={guest.name} maxLength={30} onChange={event => onRename(event.target.value)} placeholder={`Guest ${guest.id.slice(-1)}`} /></label>
    <p className="fp-body-copy">Take turns on this laptop. Like recipes you’d reach for, or pass on a specific recipe. Choices save as you go, only to this guest—not your Tasteprint. Click the same choice again to clear it.</p>
    <div className="mm-editor-toolbar"><div className="filters" role="group" aria-label="Guest recipe collection">{([['reviewed', 'Reviewed collection'], ['all', 'All model recipes'], ['choices', 'Recorded choices']] as const).map(([id, title]) => <button key={id} type="button" aria-pressed={filter === id} onClick={() => { setFilter(id); setLimit(12); }}>{title}</button>)}</div>
      <label className="search"><Search size={16} aria-hidden="true" /><span className="sr-only">Search recipes for {name}</span><input type="search" placeholder="Search dishes or ingredients" value={query} onChange={event => { setQuery(event.target.value); setLimit(12); }} /></label></div>
    <div className="fp-recipe-grid mm-guest-grid">{dishes.slice(0, limit).map(dish => <article className="fp-recipe" key={dish.id}>
      <div className="fp-recipe-image"><DishImage dish={dish} /></div><div className="fp-recipe-meta"><span>{dish.category} · {formatRecipeTime(dish.totalMinutes)}</span></div>
      <h3>{dish.name}</h3><p>{dish.description}</p><details className="ingredient-evidence"><summary>Listed ingredients and source</summary><p>{dish.ingredients.join(', ')}</p><a href={dish.sourceUrl} target="_blank" rel="noreferrer" className="small-link">Original Food.com recipe <ArrowUpRight size={12} aria-hidden="true" /></a></details>
      <OpinionButtons dish={dish} personName={name} opinion={guest.opinions[dish.id]} onPick={opinion => onPick(dish.id, opinion)} />
    </article>)}</div>
    {!dishes.length && <p className="fp-body-copy">No recipes here yet. Try another search or open the reviewed collection.</p>}
    <div className="mm-editor-footer"><p className="evidence-note">Showing {Math.min(limit, dishes.length)} of {dishes.length.toLocaleString()} recipes. Photos may be missing; ingredients are not allergy guidance.</p>
      {limit < dishes.length && <button type="button" className="button secondary" onClick={() => setLimit(value => value + 12)}>Show 12 more</button>}
      {!!Object.keys(guest.opinions).length && <button type="button" className="text-link" onClick={onClear}>Clear this guest’s choices</button>}</div>
  </section>;
}
