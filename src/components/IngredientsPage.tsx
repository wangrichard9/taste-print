import { useState, type FormEvent } from 'react';
import { ArrowRight, ArrowUpRight, Fingerprint, Plus, Utensils, X } from 'lucide-react';
import type { Dish } from '../data/catalog';
import { describeTaste, type TasteState } from '../lib/taste';
import { addIngredientNames, type IngredientRequest } from '../lib/ingredients';
import { useIngredientRecommendations } from '../lib/useIngredientRecommendations';
import IngredientResults from './IngredientResults';

const priorities = [
  { id: 'balanced', title: 'A little of both', description: 'More matches first; taste leads within the same coverage.' },
  { id: 'ingredients', title: 'Ingredients first', description: 'More matches, then fewer other listed ingredients, then taste.' },
  { id: 'taste', title: 'Taste first', description: 'Taste leads, but every recipe must match at least one ingredient.' },
] as const;

export default function IngredientsPage({ taste, onOpenDish }: { taste: TasteState; onOpenDish: (dish: Dish, previewOnly?: boolean) => void }) {
  const [ingredients, setIngredients] = useState<string[]>([]);
  const [draft, setDraft] = useState('');
  const [error, setError] = useState('');
  const [priority, setPriority] = useState<typeof priorities[number]['id']>('balanced');
  const [request, setRequest] = useState<IngredientRequest | null>(null);
  const results = useIngredientRecommendations(request, taste);
  const summary = describeTaste(taste.opinions);
  const hasDraft = draft.split(',').some(value => value.trim());
  const add = (raw: string): boolean => {
    try {
      setIngredients(addIngredientNames(ingredients, raw)); setError(''); setRequest(null); return true;
    } catch (problem) { setError((problem as Error).message); return false; }
  };
  const submitIngredient = (event: FormEvent) => { event.preventDefault(); if (add(draft)) setDraft(''); };
  const findRecipes = () => {
    try {
      const next = addIngredientNames(ingredients, draft);
      if (!next.length) return;
      setIngredients(next); setDraft(''); setError(''); setRequest({ ingredients: next, priority });
    } catch (problem) { setError((problem as Error).message); }
  };
  return <div className="feature-page">
    <section className="intro"><div><span className="eyebrow">INGREDIENTS, WITH A LITTLE INSTINCT</span><h1>Start with what <span>you have.</span></h1><p>A few things in your kitchen. A meal that feels like you.</p></div><span className="fp-page-number">02 / INGREDIENTS</span></section>
    <div className="fp-kitchen-layout"><section className="fp-kitchen-editor"><div className="section-heading"><h2>What’s in your kitchen?</h2><Utensils size={23} strokeWidth={1.3} aria-hidden="true" /></div><p className="fp-body-copy">Find recipes with at least one ingredient from your list. Extra ingredients are allowed.</p>
      <form className="fp-ingredient-form" onSubmit={submitIngredient}><label htmlFor="ingredient-entry">Add an ingredient</label><div><input id="ingredient-entry" value={draft} maxLength={180} placeholder="e.g. tomatoes, spinach, chickpeas" aria-describedby="ingredient-help" onChange={event => { setDraft(event.target.value); setError(''); setRequest(null); }} /><button type="submit" className="button secondary" disabled={!hasDraft}><Plus size={16} aria-hidden="true" /> Add</button></div><p id="ingredient-help">Press Enter to add. Separate ingredients with commas. This list lasts while this page is open.</p></form>
      {error && <p className="fp-field-error" role="alert">{error}</p>}
      <div className="fp-pantry" aria-label="Your ingredient list">{ingredients.length ? ingredients.map(ingredient => <span className="fp-ingredient-chip" key={ingredient.toLocaleLowerCase()}>{ingredient}<button type="button" aria-label={`Remove ${ingredient}`} onClick={() => { setIngredients(items => items.filter(item => item !== ingredient)); setRequest(null); setError(''); }}><X size={14} aria-hidden="true" /></button></span>) : <p>Your ingredients will gather here.</p>}</div>
      <div className="fp-pantry-actions"><span className="small-label">{ingredients.length} / 12 ingredients</span>{(ingredients.length > 0 || draft) && <button type="button" className="text-link" onClick={() => { setIngredients([]); setDraft(''); setError(''); setRequest(null); }}>Clear list</button>}</div>
      <div className="fp-suggestions"><span className="small-label">A little inspiration</span>{['Tomatoes', 'Spinach', 'Chickpeas', 'Rice'].map(item => <button key={item} type="button" disabled={ingredients.some(value => value.toLocaleLowerCase() === item.toLocaleLowerCase())} onClick={() => add(item)}><Plus size={12} aria-hidden="true" /> {item}</button>)}</div>
      <fieldset className="fp-priority"><legend>What matters most tonight?</legend><p>Choose how ingredients and taste order your options.</p><div>{priorities.map(option => <button type="button" key={option.id} aria-pressed={priority === option.id} onClick={() => { setPriority(option.id); if (request) setRequest({ ...request, priority: option.id }); }}>{option.title}</button>)}</div><span>{priorities.find(option => option.id === priority)!.description}</span></fieldset>
      <button type="button" className="button primary fp-preview-action" disabled={!ingredients.length && !hasDraft} onClick={findRecipes}>Find recipes <ArrowRight size={17} aria-hidden="true" /></button>
    </section><aside className="fp-kitchen-taste"><div className="fp-taste-orbit" aria-hidden="true"><span /><span /><Fingerprint size={78} strokeWidth={1} /></div><span className="eyebrow">YOUR TASTE, ALONG FOR THE RIDE</span><h2>More than<br />an ingredient list.</h2><p>Your likes bring shared-like evidence into the ranking. Without that evidence, popularity helps order ingredient matches.</p><div className="fp-tag-row">{summary.patterns.map(pattern => pattern.tag).map(tag => <span key={tag}>{tag}</span>)}</div><p className="evidence-note">{summary.patterns.length ? 'These tags describe your likes; they are not ranking features.' : 'Like a few recipes in Discover to bring your preferences into the ranking. Saves alone do not change ranking.'} New ideas and matching favorites stay separate. New does not necessarily mean niche.</p><a className="text-link" href="#tasteprint">Your Tasteprint <ArrowUpRight size={16} aria-hidden="true" /></a></aside></div>
    <section className="fp-ingredient-results" aria-live="polite" aria-busy={results.status === 'loading'}>
      {results.status === 'loading' && <p className="fp-body-copy" role="status">Matching your list and ranking recipe options…</p>}
      {(results.status === 'error' || results.status === 'invalid') && <div className="fp-result-placeholder"><div><h2>{results.status === 'invalid' ? 'Check your ingredient list.' : 'Couldn’t load results from the local recipe service.'}</h2><p>{results.status === 'invalid' ? 'Use ingredient names rather than preparation-only words such as “chopped.” Keep to 12 names, up to 40 characters each, then try again.' : 'No sample matches are being shown. Check that the local model service is running and try again.'}</p></div><button type="button" className="button secondary" onClick={results.retry}>Try again</button></div>}
      {results.status === 'ready' && results.result && <IngredientResults key={JSON.stringify(request) + JSON.stringify(taste.opinions)} result={results.result} onOpenDish={onOpenDish} />}
      {results.status === 'idle' && <div className="fp-result-placeholder"><span>01</span><div><h2>Your kitchen, then a little possibility.</h2><p>Add ingredients, then find real recipes with room for discovery.</p></div><button type="button" className="text-link" onClick={() => { setIngredients(['Tomatoes', 'Spinach', 'Chickpeas']); setDraft(''); setError(''); setRequest(null); }}>Use example ingredients <ArrowRight size={16} aria-hidden="true" /></button></div>}
    </section>
  </div>;
}
