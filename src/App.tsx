import { useEffect, useState } from 'react';
import { ArrowUpRight, ArrowRight, Bookmark, Search, ThumbsUp, ThumbsDown, Users, RefreshCw } from 'lucide-react';
import { catalog, formatRecipeTime, type Dish } from './data/catalog';
import { describeTaste, setOpinion, toggleSaved, type BrowseFilter } from './lib/taste';
import { discoveryDishes, recommendationReason } from './lib/discovery';
import { useRecommendations } from './lib/useRecommendations';
import { useTaste } from './lib/useTaste';
import Dialog from './components/Dialog';
import DishImage from './components/DishImage';
import Onboarding, { OpinionButtons } from './components/Onboarding';
import LandingPage from './components/LandingPage';
import TasteProfilePage from './components/TasteProfilePage';
import IngredientsPage from './components/IngredientsPage';
import MealMergePage from './components/MealMergePage';
import SourceDirections from './components/SourceDirections';
import AppNavigation from './components/AppNavigation';
import './features.css';

type Page = 'home' | 'discover' | 'tasteprint' | 'ingredients' | 'mealmerge';
function readPage(): Page {
  const page = window.location.hash.slice(1);
  return page === 'discover' || page === 'tasteprint' || page === 'ingredients' || page === 'mealmerge' ? page : 'home';
}

export default function App() {
  const { taste, setTaste, storageWarning } = useTaste();
  const [page, setPage] = useState<Page>(readPage);
  const [filter, setFilter] = useState<BrowseFilter>('all');
  const [query, setQuery] = useState('');
  const [onboarding, setOnboarding] = useState(false);
  const [selectedDish, setSelectedDish] = useState<Dish | null>(null);
  const [previewOnly, setPreviewOnly] = useState(false);
  const [notice, setNotice] = useState('');
  const [visibleCount, setVisibleCount] = useState(24);
  const recommendations = useRecommendations(taste, page === 'discover');
  useEffect(() => { setVisibleCount(24); }, [query, filter, taste.opinions]);
  useEffect(() => {
    const update = () => { setPage(readPage()); window.scrollTo({ top: 0, behavior: 'instant' }); };
    window.addEventListener('hashchange', update);
    return () => window.removeEventListener('hashchange', update);
  }, []);
  const summary = describeTaste(taste.opinions);
  const dishes = discoveryDishes(recommendations.result, taste, query, filter);
  const evidenceById = new Map(recommendations.result?.items.map(item => [item.id, item]));
  const openDish = (dish: Dish, sample = false) => { setPreviewOnly(sample); setSelectedDish(dish); };
  const save = (dish: Dish) => {
    setTaste(previous => toggleSaved(previous, dish.id));
    setNotice(`${dish.name} ${taste.saved.includes(dish.id) ? 'removed from favorites' : 'saved to favorites'}.`);
  };
  const pick = (dish: Dish, opinion: 'like' | 'pass') => {
    setTaste(previous => setOpinion(previous, dish.id, opinion));
    setNotice(taste.opinions[dish.id] === opinion ? `Opinion cleared for ${dish.name}.`
      : `${dish.name}: ${opinion === 'like' ? 'liked' : 'not for you'}.`);
  };

  return <>
    <a className="skip-link" href="#main-content" onClick={event => {
      event.preventDefault(); document.getElementById('main-content')?.focus();
    }}>Skip to content</a>
    {page !== 'home' && <AppNavigation page={page} />}
    <main id="main-content" tabIndex={-1} className={page === 'home' ? 'landing-main' : 'app-main'}>
      {storageWarning && <p className="storage-warning" role="alert">{storageWarning}</p>}
      <div key={page} className={page === 'home' ? 'landing-route' : 'page-arrival'}>
      {page === 'home' && <LandingPage taste={taste} onStart={() => setOnboarding(true)} onPick={pick} />}
      {page === 'discover' && <>
        <section className="intro"><div><span className="eyebrow">A little more your taste.</span>
          <h1>Find your next <span>favourite.</span></h1><p>Good food. A fresh perspective on what you love.</p></div>
          <button className="button primary" type="button" onClick={() => setOnboarding(true)}>Refine your taste <ArrowUpRight size={17} aria-hidden="true" /></button>
        </section>
        <section className="recommendation-status" aria-label="Recommendation status" aria-busy={recommendations.status === 'loading'}>
          <div className="recommendation-summary" aria-live="polite">
          {recommendations.status === 'loading' ? <p role="status">Connecting your choices to the local model… You can browse the catalog while it loads.</p>
            : recommendations.status === 'error' ? <div role="alert"><p>Recommendations are unavailable. You’re browsing catalog order, not personalized results. Your choices are still saved.</p>
              <p className="evidence-note">Start the local model with <code>npm run dev:model</code>, then <button type="button" className="text-link" onClick={recommendations.retry}>retry recommendations</button>.</p></div>
            : recommendations.result?.mode === 'co_like' ? <><span className="eyebrow">FROM YOUR LIKES · CO-LIKE CF</span>
              <p>Ranked from {recommendations.result.supportedLikeCount} liked {recommendations.result.supportedLikeCount === 1 ? 'recipe' : 'recipes'} and historical shared likes. Already liked or passed dishes are left out.</p>
              <p className="evidence-note">Popularity-heavy by design. This experiment was evaluated with six likes; a shorter or longer profile is supported but has not been separately validated. Saves don’t affect ranking.</p></>
            : <><span className="eyebrow">POPULAR PICKS · NOT PERSONALIZED</span><p>{recommendations.result?.supportedLikeCount ? 'Your likes have no shared-like evidence for remaining recipes. Showing popular choices instead.' : 'Like a recipe to start personalizing. For now, these are popular choices from the fitting data.'}</p></>}
          {recommendations.status === 'ready' && recommendations.updatedAt !== null && <p className="recommendation-updated" role="status">
            Updated at {new Date(recommendations.updatedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })} · Your latest choices are applied.
          </p>}
          </div>
          <div className="recommendation-actions">
            <button className="button secondary" type="button" aria-label="Refresh recommendations"
              disabled={recommendations.status === 'loading'} onClick={() => { setVisibleCount(24); recommendations.retry(); }}>
              <RefreshCw size={15} aria-hidden="true" /> {recommendations.status === 'loading' ? 'Refreshing…' : 'Refresh recommendations'}
            </button>
            <p>Likes update automatically. Refresh reruns your latest choices; the order may stay similar.</p>
          </div>
        </section>
        <div className="toolbar"><div className="filters" role="group" aria-label="Filter dishes">
          {([['all', 'All dishes'], ['fresh', 'Fresh & bright'], ['comfort', 'Comfort food'], ['saved', `Saved${taste.saved.length ? ` (${taste.saved.length})` : ''}`]] as const).map(([id, label]) =>
            <button key={id} type="button" aria-pressed={filter === id} onClick={() => setFilter(id)}>{label}</button>)}
        </div><label className="search"><Search size={17} aria-hidden="true" /><span className="sr-only">Search dishes and ingredients</span>
          <input type="search" placeholder="Search dishes or ingredients" value={query} onChange={event => setQuery(event.target.value)} />
        </label></div>
        <div className="discovery-layout">
          <section aria-label="Dish results" className="dish-grid">
            {dishes.slice(0, visibleCount).map((dish, index) => <article className="dish-card" key={dish.id}>
              <button className="dish-photo" type="button" aria-label={`View ${dish.name}`} onClick={() => openDish(dish)}>
                <DishImage dish={dish} eager={index < 2} />
                <span className="image-caption">{dish.tags[0]}</span>
              </button>
              <div className="dish-meta"><span>{dish.category} · {formatRecipeTime(dish.totalMinutes)}</span>
                <button className="save-button" type="button" aria-pressed={taste.saved.includes(dish.id)}
                  aria-label={`${taste.saved.includes(dish.id) ? 'Unsave' : 'Save'} ${dish.name}`} onClick={() => save(dish)}>
                  <Bookmark size={15} aria-hidden="true" fill={taste.saved.includes(dish.id) ? 'currentColor' : 'none'} /> {taste.saved.includes(dish.id) ? 'Saved' : 'Save'}
                </button></div>
              <h2><button type="button" onClick={() => openDish(dish)}>{dish.name}</button></h2>
              <p>{dish.description}</p>
              {filter !== 'saved' && evidenceById.has(dish.id) && <p className="recommendation-evidence">{recommendationReason(evidenceById.get(dish.id)!)}</p>}
              {taste.opinions[dish.id] && <span className="recorded-opinion">{taste.opinions[dish.id] === 'like' ? <ThumbsUp size={13} aria-hidden="true" /> : <ThumbsDown size={13} aria-hidden="true" />}
                {taste.opinions[dish.id] === 'like' ? 'You like this' : 'Not for you'}</span>}
            </article>)}
            {!dishes.length && <div className="empty-state"><Bookmark size={27} aria-hidden="true" /><h2>{filter === 'saved' && !query ? 'Make a little collection.' : 'Nothing here just yet.'}</h2>
              <p>{filter === 'saved' && !query ? 'Save a dish that catches your eye. You’ll find it here.' : 'Try a different ingredient, or open up your filters.'}</p>
              <button type="button" className="button secondary" onClick={() => { setQuery(''); setFilter('all'); }}>Browse all dishes <ArrowRight size={16} aria-hidden="true" /></button></div>}
          </section>
          <aside className="discovery-aside">
            <a className="merge-card" href="#mealmerge"><span className="eyebrow">MEALMERGE · YOUR LOCAL TABLE</span>
              <Users size={27} strokeWidth={1.4} aria-hidden="true" /><h2>Different tastes.<br />One good meal.</h2>
              <p>Bring everyone’s preferences to the table.</p><span className="merge-link">Find shared recipes <ArrowUpRight size={18} aria-hidden="true" /></span></a>
            <section className="side-note"><span className="eyebrow">YOUR TASTE, IN FOCUS</span>
              <h2>{summary.liked.length + summary.passed.length ? 'A few choices.\nA clearer starting point.' : 'It starts with\nwhat you love.'}</h2>
              <p>{summary.liked.length + summary.passed.length ? `${summary.liked.length} liked · ${summary.passed.length} not for you. Your choices are saved locally.` : 'Tell us which dishes you’d reach for. We’ll keep your choices in one place.'}</p>
              <a className="text-link" href="#tasteprint">Your Tasteprint <ArrowRight size={16} aria-hidden="true" /></a>
            </section>
            <div className="catalog-note"><span className="small-label">THE MODEL COLLECTION</span><p>5,006 Food.com recipes, not the full dataset. Our original 30 are manually reviewed; the rest use source metadata. Photos may be missing.</p><p>Fresh & bright and Comfort food are editorial labels on the reviewed collection, not learned classifications.</p><a className="small-link" href={catalog[0].datasetUrl} target="_blank" rel="noreferrer">Dataset & attribution <ArrowUpRight size={12} aria-hidden="true" /></a></div>
          </aside>
        </div>
        <div className="discovery-pagination"><p className="results-status" role="status">Showing {Math.min(visibleCount, dishes.length)} of {dishes.length} matching recipes · {catalog.length.toLocaleString()} in the catalog · {filter === 'saved' ? 'your saved collection' : recommendations.status !== 'ready' ? 'catalog order' : recommendations.result?.mode === 'co_like' ? 'shared-like ranking, then popularity where evidence is missing' : 'popularity order'}</p>
          {visibleCount < dishes.length && <button className="button secondary" type="button" onClick={() => setVisibleCount(value => value + 24)}>Show 24 more <ArrowRight size={16} aria-hidden="true" /></button>}</div>
      </>}
      {page === 'tasteprint' && <TasteProfilePage taste={taste} onEdit={() => setOnboarding(true)} onOpenDish={openDish} onUnsave={save} />}
      {page === 'ingredients' && <IngredientsPage taste={taste} onOpenDish={openDish} />}
      {page === 'mealmerge' && <MealMergePage taste={taste} onOpenDish={openDish} />}
      </div>
      {page !== 'home' && <footer className="app-footer"><span>tasteprint<span className="blue-text">.</span> <span className="footer-separator">/</span> LOCAL DEMO · SOURCE RECIPES</span>
        <span>Food.com via irkaal · local co-like Discover, Ingredients & MealMerge · no dietary guarantees</span></footer>}
    </main>
    <div className="sr-only" role="status" aria-live="polite">{notice}</div>
    {onboarding && <Onboarding taste={taste} onClose={() => setOnboarding(false)} onComplete={opinions => {
      setTaste(previous => ({ ...previous, opinions, onboarded: true })); setOnboarding(false);
      setNotice('Your choices are saved locally. Discover is updating from your likes.'); window.location.hash = 'discover';
    }} />}
    {selectedDish && <Dialog titleId="dish-dialog-title" onClose={() => setSelectedDish(null)}>
      <div className="detail-image"><DishImage dish={selectedDish} eager /></div><div className="detail-body">
        <span className="eyebrow">{selectedDish.category} · FOOD.COM RECIPE</span><h1 id="dish-dialog-title">{selectedDish.name}</h1><p>{selectedDish.description}</p>
        <div className="recipe-facts"><span>Source time: {formatRecipeTime(selectedDish.totalMinutes)}</span>{selectedDish.servings !== null && selectedDish.servings > 0 && <span>Source servings: {selectedDish.servings}</span>}</div>
        <div className="tag-list">{selectedDish.tags.map(tag => <span key={tag}>{tag}</span>)}</div>
        {previewOnly ? <p className="fp-detail-preview">Opened from a sample preview. Viewing this recipe doesn’t change your Tasteprint.</p> : <><h2>Would you reach for this?</h2><OpinionButtons dish={selectedDish} opinion={taste.opinions[selectedDish.id]} onPick={opinion => pick(selectedDish, opinion)} />
        <button type="button" className="button secondary detail-save" aria-pressed={taste.saved.includes(selectedDish.id)} onClick={() => save(selectedDish)}>
          <Bookmark size={16} aria-hidden="true" /> {taste.saved.includes(selectedDish.id) ? 'Remove from saved' : 'Save for later'}</button></>}
        <h2>Listed ingredients</h2><ul className="ingredient-list">{selectedDish.ingredients.map((ingredient, index) => <li key={`${ingredient}-${index}`}>{ingredient}</li>)}</ul>
        <p className="evidence-note">Dataset ingredients may be incomplete. Amounts and units are not included here; consult the original recipe before cooking. Ingredients are not allergy guidance.</p>
        <SourceDirections key={selectedDish.id} dish={selectedDish} />
        <p className="evidence-note">Source instructions and reported times are preserved, not kitchen-tested by Tasteprint. “Not for me” records a preference, not an allergy.</p>
        <div className="recipe-attribution"><a className="small-link" href={selectedDish.sourceUrl} target="_blank" rel="noreferrer">Original recipe & photo source <ArrowUpRight size={12} aria-hidden="true" /></a>
          <a className="small-link" href={selectedDish.datasetUrl} target="_blank" rel="noreferrer">Dataset: irkaal · version {selectedDish.datasetVersion} <ArrowUpRight size={12} aria-hidden="true" /></a></div>
        <p className="evidence-note">Original title: {selectedDish.sourceName}. {selectedDish.manuallyReviewed ? 'Part of the 30 manually reviewed recipes; display names, summaries and taste tags are editorial.' : 'Bulk-imported source metadata, not manually reviewed. The category tag comes from Food.com; the short collection description is a display label.'} Recipe and any photo are from Food.com contributors.</p>
      </div>
    </Dialog>}
  </>;
}
