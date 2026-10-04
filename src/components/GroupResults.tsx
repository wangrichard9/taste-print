import { useState } from 'react';
import { ArrowUpRight } from 'lucide-react';
import { dishById, formatRecipeTime, type Dish } from '../data/catalog';
import { memberReason, type GroupResult } from '../lib/mealmerge';
import DishImage from './DishImage';

export default function GroupResults({ result, onOpenDish }: { result: GroupResult; onOpenDish: (dish: Dish) => void }) {
  const [view, setView] = useState<'picks' | 'comparison'>('picks');
  const [limit, setLimit] = useState(12);
  const items = result.items.slice(0, limit);
  return <>
    <div className="section-heading"><div><span className="eyebrow">ACTUAL OPTIONS, INDIVIDUAL EVIDENCE</span><h2>Something for the table.</h2></div><span className="fp-sample-label">{result.items.length.toLocaleString()} eligible recipes</span></div>
    <p className="fp-results-context">{result.priority === 'balanced' ? 'Balanced compromise' : 'Overall appeal'} · broader evidence first · {result.excludedCount} recipes left out because someone passed.</p>
    <p className="evidence-note mm-result-note">Personal evidence exists for {result.evidenceMemberCount} of {result.members.length} people; the strongest coverage for one recipe is {result.maxSupportCount} of {result.members.length}. Missing evidence is unknown, not a dislike. Positions describe recommendation order—not satisfaction or safety. Recipe-detail likes/saves affect your own Tasteprint, not a guest.</p>
    {result.evidenceMemberCount === 0 ? <p className="mm-group-status" role="status">No usable personal evidence for these options. Both priorities show training popularity as a fallback, not a group taste prediction.</p> : result.evidenceMemberCount < result.members.length && <p className="mm-group-status" role="status">Some people have no evidence for the remaining options. Their preferences remain unknown; the two priorities may agree. Add guest likes to give them a voice in ranking.</p>}
    <div className="fp-view-switch" role="group" aria-label="MealMerge results view"><button type="button" aria-pressed={view === 'picks'} onClick={() => setView('picks')}>Shared meal ideas</button><button type="button" aria-pressed={view === 'comparison'} onClick={() => setView('comparison')}>Per-person evidence</button></div>
    {!items.length && <p className="fp-body-copy">No recipes remain after the table’s passes. Edit recorded choices to reconsider specific recipes.</p>}
    {view === 'picks' ? <div className="fp-recipe-grid">{items.map(item => {
      const dish = dishById.get(item.id)!;
      return <article className="fp-recipe mm-result-card" key={item.id}>
        <button type="button" className="fp-recipe-image" onClick={() => onOpenDish(dish)} aria-label={`View ${dish.name}`}><DishImage dish={dish} /><span>{item.basis === 'popularity' ? 'Popularity fallback' : `${item.supportCount} of ${result.members.length} with evidence`}</span><ArrowUpRight size={18} aria-hidden="true" /></button>
        <div className="fp-recipe-meta"><span>{dish.category} · {formatRecipeTime(dish.totalMinutes)}</span></div><h3><button type="button" onClick={() => onOpenDish(dish)}>{dish.name}</button></h3>
        <ul className="mm-member-evidence">{item.members.map((row, i) => <li key={row.memberId}><strong>{result.members[i].name}</strong><span>{row.basis === 'known_like' ? 'Already liked' : row.basis === 'unknown' ? 'Unknown · not a dislike' : `Shared-like position ${row.position!.toLocaleString()} / ${result.members[i].coLikeCount.toLocaleString()}`}</span></li>)}</ul>
        <details className="ingredient-evidence"><summary>Where the evidence comes from</summary>{item.members.map((row, i) => <p key={row.memberId}><strong>{result.members[i].name}:</strong> {memberReason(row, result.members[i].coLikeCount)}</p>)}{item.basis === 'popularity' && <p>Ordered by training popularity; no member has personal evidence for this recipe.</p>}</details>
      </article>;
    })}</div> : <div className="fp-comparison-scroll" tabIndex={0} role="region" aria-label="Scrollable per-person recipe evidence"><table className="fp-comparison"><caption>Evidence behind this group order, not predicted satisfaction</caption><thead><tr><th scope="col">Recipe</th>{result.members.map(member => <th scope="col" key={member.id}>{member.name}</th>)}</tr></thead><tbody>{items.map(item => <tr key={item.id}><th scope="row"><button type="button" onClick={() => onOpenDish(dishById.get(item.id)!)}>{dishById.get(item.id)!.name}<ArrowUpRight size={13} aria-hidden="true" /></button></th>{item.members.map((row, i) => <td key={row.memberId}>{memberReason(row, result.members[i].coLikeCount)}</td>)}</tr>)}</tbody></table></div>}
    {limit < result.items.length && <button type="button" className="button secondary ingredient-more" onClick={() => setLimit(value => value + 12)}>Show 12 more ({result.items.length - limit} remaining)</button>}
  </>;
}
