import { useState } from 'react';
import { ArrowRight, Fingerprint, Plus, Users, X } from 'lucide-react';
import type { Dish } from '../data/catalog';
import { describeTaste, type TasteState } from '../lib/taste';
import { groupRequest, guestOpinion, newGuest, type GroupPriority } from '../lib/mealmerge';
import { useMealMergeGuests } from '../lib/useMealMergeGuests';
import { useGroupRecommendations } from '../lib/useGroupRecommendations';
import GuestEditor from './GuestEditor';
import GroupResults from './GroupResults';

export default function MealMergePage({ taste, onOpenDish }: { taste: TasteState; onOpenDish: (dish: Dish, previewOnly?: boolean) => void }) {
  const { guests, setGuests, warning } = useMealMergeGuests();
  const [editing, setEditing] = useState<string | null>(null);
  const [compared, setCompared] = useState(false);
  const [priority, setPriority] = useState<GroupPriority>('balanced');
  const summary = describeTaste(taste.opinions);
  const request = compared && guests.length ? groupRequest(taste, guests, priority) : null;
  const results = useGroupRecommendations(request);
  const editor = guests.find(guest => guest.id === editing);
  const addGuest = () => {
    const id = ['guest-1', 'guest-2', 'guest-3'].find(value => !guests.some(guest => guest.id === value));
    if (!id) return;
    setGuests(previous => [...previous, newGuest(id)]); setEditing(id); setCompared(false);
  };
  return <div className="feature-page">
    <section className="intro"><div><span className="eyebrow">MEALMERGE · BRING YOUR TASTES TOGETHER</span><h1>Different tastes.<br />One <span>good meal.</span></h1><p>A shared table. A little less “what do you want?”</p></div><span className="fp-page-number">03 / TOGETHER</span></section>
    <div className="fp-group-intro"><div><span className="eyebrow">THE TABLE STARTS HERE</span><h2>Who’s joining you?</h2><p>Your Tasteprint plus up to three local guests. No accounts, invitations or shared online profiles.</p></div><span className="fp-group-count"><Users size={19} aria-hidden="true" /> {guests.length + 1} at the table</span></div>
    {warning && <p className="mm-group-status" role="status">{warning}</p>}
    <div className="fp-people-grid"><article className="fp-person is-at-table"><span className="fp-person-top"><span className="fp-person-avatar"><Fingerprint size={23} aria-hidden="true" /></span></span><h2 className="fp-person-name">You</h2><p className="fp-person-subtitle">{summary.liked.length} liked · {summary.passed.length} passed. Your existing Tasteprint.</p><a href="#tasteprint" className="text-link">Edit your recorded choices</a></article>
      {guests.map(guest => {
        const name = guest.name.trim() || `Guest ${guest.id.slice(-1)}`;
        const liked = Object.values(guest.opinions).filter(opinion => opinion === 'like').length;
        const passed = Object.values(guest.opinions).filter(opinion => opinion === 'pass').length;
        return <article className="fp-person is-at-table" key={guest.id}><div className="fp-person-top"><span className="fp-person-avatar">{name.slice(0, 1)}</span><button type="button" className="icon-button" aria-label={`Remove ${name} and their guest choices`} onClick={() => { setGuests(previous => previous.filter(person => person.id !== guest.id)); if (editing === guest.id) setEditing(null); setCompared(false); }}><X size={16} aria-hidden="true" /></button></div><h2 className="fp-person-name">{name}</h2><p className="fp-person-subtitle">{liked} liked · {passed} passed. {liked ? 'Real recipe opinions.' : 'Taste unknown until likes are added.'}</p><button type="button" className="text-link" aria-expanded={editing === guest.id} onClick={() => { setEditing(editing === guest.id ? null : guest.id); setCompared(false); }}>Edit guest choices</button></article>;
      })}
      {guests.length < 3 && <button type="button" className="fp-person mm-add-person" onClick={addGuest}><Plus size={24} aria-hidden="true" /><span className="fp-person-name">Add a guest</span><span className="fp-person-subtitle">Their choices stay separate from yours.</span></button>}
    </div>
    {editor && <GuestEditor key={editor.id} guest={editor} onRename={name => { setGuests(previous => previous.map(guest => guest.id === editor.id ? { ...guest, name } : guest)); setCompared(false); }}
      onPick={(id, opinion) => { setGuests(previous => guestOpinion(previous, editor.id, id, opinion)); setCompared(false); }}
      onClear={() => { setGuests(previous => previous.map(guest => guest.id === editor.id ? { ...guest, opinions: {} } : guest)); setCompared(false); }}
      onDone={() => setEditing(null)} />}
    <fieldset className="fp-priority mm-group-priority"><legend>How should the table decide?</legend><p>Broader personal evidence comes first in both modes; unknown entries are not scored as dislikes.</p><div><button type="button" aria-pressed={priority === 'balanced'} onClick={() => setPriority('balanced')}>Balanced compromise</button><button type="button" aria-pressed={priority === 'overall'} onClick={() => setPriority('overall')}>Overall appeal</button></div><span>{priority === 'balanced' ? 'Favor the weakest supported relative position, then the average. Not a guarantee everyone will like it.' : 'Favor the average supported relative position, then the weakest. Not a measured satisfaction score.'}</span></fieldset>
    <div className="fp-group-bottom"><p>Guest choices stay in this browser until you clear or remove them. Anyone’s pass leaves that recipe out—not its ingredients. At least one guest is needed.</p><button type="button" className="button primary" disabled={!guests.length} onClick={() => { setEditing(null); setCompared(true); }}>Find shared recipes <ArrowRight size={16} aria-hidden="true" /></button></div>
    <section className="mm-group-results" aria-live="polite" aria-busy={results.status === 'loading'}>
      {results.status === 'loading' && <p className="fp-body-copy" role="status">Comparing your table’s real recipe preferences…</p>}
      {(results.status === 'error' || results.status === 'invalid') && <div className="fp-result-placeholder"><div><h2>{results.status === 'invalid' ? 'Check the table’s profiles.' : 'Couldn’t load the local group results.'}</h2><p>{results.status === 'invalid' ? 'Use one to three guests with valid names and recipe choices.' : 'Check that the local model service is running. No sample group picks are being shown.'}</p></div><button type="button" className="button secondary" onClick={results.retry}>Try again</button></div>}
      {results.status === 'ready' && results.result && <GroupResults key={JSON.stringify(request)} result={results.result} onOpenDish={onOpenDish} />}
      {results.status === 'idle' && <div className="fp-group-story"><Fingerprint size={44} strokeWidth={1.1} aria-hidden="true" /><div><span className="eyebrow">FIND THE OVERLAP. KEEP THE INDIVIDUAL.</span><h2>Give every taste a place at the table.</h2><p>Add guest likes, then find shared recipes. We’ll show what is known for each person and what is still unknown. Existing co-like evidence powers individual positions; the group policies are simple rules, not another trained model.</p></div></div>}
    </section>
  </div>;
}
