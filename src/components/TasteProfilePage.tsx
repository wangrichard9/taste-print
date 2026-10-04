import { useId, useState } from 'react';
import { LayoutGroup, MotionConfig, motion } from 'motion/react';
import { ArrowRight, ArrowUpRight, Bookmark, Fingerprint, SlidersHorizontal, ThumbsDown, ThumbsUp } from 'lucide-react';
import { catalog, type Dish } from '../data/catalog';
import { exampleTaste } from '../data/feature-previews';
import { describeTaste, type TasteState } from '../lib/taste';
import { describeSensory, sensoryHeading, sensoryNotesFor } from '../lib/sensory';
import SensoryProfile from './SensoryProfile';
import DishImage from './DishImage';
import { PreviewNotice, RecipePreviewCard } from './FeaturePreview';

type Props = { taste: TasteState; onEdit: () => void; onOpenDish: (dish: Dish, previewOnly?: boolean) => void; onUnsave: (dish: Dish) => void };
type View = 'overview' | 'choices' | 'saved';

export default function TasteProfilePage({ taste, onEdit, onOpenDish, onUnsave }: Props) {
  const [example, setExample] = useState(false);
  const [view, setView] = useState<View>('overview');
  const [choiceFilter, setChoiceFilter] = useState<'all' | 'like' | 'pass'>('all');
  const viewGroup = useId();
  const profile = example ? exampleTaste : taste;
  const summary = describeTaste(profile.opinions);
  const sensory = describeSensory(profile.opinions);
  const choices = catalog.filter(dish => profile.opinions[dish.id] && (choiceFilter === 'all' || profile.opinions[dish.id] === choiceFilter));
  const saved = catalog.filter(dish => profile.saved.includes(dish.id));
  const total = summary.liked.length + summary.passed.length;
  const editChoices = () => { setExample(false); setView('overview'); onEdit(); };
  return <div className="feature-page">
    <section className="intro"><div><span className="eyebrow">YOUR TASTEPRINT</span><h1>A little more <span>you.</span></h1><p>Your favourites, first impressions, and room for something new.</p></div>
      <button type="button" className="button primary" onClick={editChoices}><SlidersHorizontal size={16} aria-hidden="true" />{total && !example ? 'Edit your choices' : 'Build my Tasteprint'}</button></section>
    <div className="fp-profile-mode"><p>{example ? 'You’re exploring an example Tasteprint.' : 'Your local Tasteprint. Made from your choices.'}</p><button type="button" className="text-link" aria-pressed={example} onClick={() => setExample(value => !value)}>{example ? 'Back to my Tasteprint' : 'Explore an example'} <ArrowRight size={15} aria-hidden="true" /></button></div>
    {example && <PreviewNotice>This sample profile doesn’t change your saved choices.</PreviewNotice>}
    <div className="taste-portrait-heading"><div><Fingerprint size={48} strokeWidth={1} aria-hidden="true" /><div><h2>{sensoryHeading(sensory)}</h2><p>{sensory.annotatedCount ? 'Notes from the dishes you keep coming back to.' : 'Choose a few dishes. Let your picture take shape.'}</p></div></div>
      <div className="taste-small-counts"><span><ThumbsUp size={14} aria-hidden="true" /><strong>{summary.liked.length}</strong> liked</span><span><ThumbsDown size={14} aria-hidden="true" /><strong>{summary.passed.length}</strong> passed</span><span><Bookmark size={14} aria-hidden="true" /><strong>{profile.saved.length}</strong> saved</span></div>
    </div>
    <MotionConfig reducedMotion="never"><LayoutGroup id={viewGroup}><div className="fp-view-switch gliding-view-switch" role="group" aria-label="Tasteprint view">{([['overview', 'Taste overview'], ['choices', 'Your choices'], ['saved', 'Saved dishes']] as const).map(([id, label]) => <button type="button" key={id} aria-pressed={view === id} onClick={() => setView(id)}>{label}<span>{id === 'choices' ? total : id === 'saved' ? saved.length : '01'}</span>{view === id && <motion.i aria-hidden="true" className="taste-view-indicator" layoutId="taste-view-indicator" transition={{ type: 'spring', stiffness: 390, damping: 34 }} />}</button>)}</div></LayoutGroup></MotionConfig>
    <div key={view} className="view-content-arrival">
    {view === 'overview' && <><SensoryProfile key={example ? 'example' : 'personal'} summary={sensory} example={example} onOpenDish={onOpenDish} />
      <div className="taste-profile-next"><a href="#ingredients">Find something with your ingredients <ArrowUpRight size={17} aria-hidden="true" /></a><a href="#mealmerge">Bring your tastes to the table <ArrowUpRight size={17} aria-hidden="true" /></a></div>
    </>}
    {view === 'choices' && <section className="fp-choice-list"><div className="section-heading"><h2>{example ? 'An example food journey.' : 'Your food journey.'}</h2><div className="filters" role="group" aria-label="Filter recorded choices">{([['all', 'All choices'], ['like', 'Liked'], ['pass', 'Not for me']] as const).map(([id, label]) => <button type="button" key={id} aria-pressed={choiceFilter === id} onClick={() => setChoiceFilter(id)}>{label}</button>)}</div></div>{choices.map(dish => <button type="button" className="history-row" key={dish.id} aria-label={`${example ? 'View sample dish' : 'Edit preference for'} ${dish.name}`} onClick={() => onOpenDish(dish, example)}><span className="history-image"><DishImage dish={dish} /></span><span>{dish.name}<small>{sensoryNotesFor(dish).join(' · ') || `${dish.category} · Sensory notes unassessed`}</small></span><span className={profile.opinions[dish.id] === 'like' ? 'blue-text' : 'muted'}>{profile.opinions[dish.id] === 'like' ? 'Like it' : 'Not for me'}</span><ArrowUpRight size={16} aria-hidden="true" /></button>)}{!choices.length && <div className="fp-empty"><h3>No choices in this view yet.</h3><p>Start with a few first impressions, or try another filter.</p><button type="button" className="button secondary" onClick={editChoices}>Choose a few dishes</button></div>}</section>}
    {view === 'saved' && <section><div className="section-heading"><h2>{example ? 'A sample little collection.' : 'For another day.'}</h2><a className="text-link" href="#discover">Keep exploring <ArrowUpRight size={15} aria-hidden="true" /></a></div>{saved.length ? <div className="fp-recipe-grid">{saved.map(dish => <RecipePreviewCard dish={dish} key={dish.id} onOpen={() => onOpenDish(dish, example)} onUnsave={example ? undefined : () => onUnsave(dish)} />)}</div> : <div className="fp-empty"><Bookmark size={28} aria-hidden="true" /><h3>Your own little collection.</h3><p>Save recipes in Discover and come back to them here.</p><a className="button secondary" href="#discover">Explore recipes <ArrowRight size={15} aria-hidden="true" /></a></div>}</section>}
    </div>
  </div>;
}
