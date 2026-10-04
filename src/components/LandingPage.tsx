import { lazy, Suspense, useEffect, useRef, useState } from 'react';
import { motion, useInView } from 'motion/react';
import { ArrowRight, ArrowUp, ArrowUpRight, Check, Fingerprint, Play, ThumbsUp, Utensils, X } from 'lucide-react';
import { catalog, onboardingDishes, formatRecipeTime, type Dish } from '../data/catalog';
import { describeTaste, type Opinion, type TasteState } from '../lib/taste';
import DishImage from './DishImage';
import { OpinionButtons } from './Onboarding';
import StarBorder from './react-bits/StarBorder';
import '../landing.css';
import '../landing-immersive.css';

const RippleDistortion = lazy(() => import('./react-bits/RippleDistortion'));
const ScrollReveal = lazy(() => import('./react-bits/ScrollReveal'));
const choices = onboardingDishes.slice(0, 3);
const stages = ['Food choices', 'Your Tasteprint', 'Discover'];
const demoLikes: Record<string, Opinion> = { [choices[0].id]: 'like', [choices[1].id]: 'like', [choices[2].id]: 'pass' };

function ProductScene({ phase, opinions }: { phase: number; opinions: Record<string, Opinion> }) {
  const summary = describeTaste(opinions);
  return <div className="product-scene" aria-hidden="true">
    <div className="scene-grid" />
    <span className="scene-coordinate">A LITTLE MORE YOU ↗</span>
    {[0, 1, 2].map(index => {
      const depth = (index - phase + 3) % 3;
      return <motion.div key={index} className={`scene-panel panel-${index}`} animate={{
        x: depth === 0 ? '0%' : depth === 1 ? '12%' : '-7%',
        y: depth === 0 ? 0 : depth === 1 ? -35 : 40,
        rotate: depth === 0 ? -2 : depth === 1 ? 5 : -7,
        scale: depth === 0 ? 1 : 0.95,
      }} transition={{ duration: 0.75, ease: [0.22, 1, 0.36, 1] }} style={{ zIndex: 3 - depth }}>
        <div className="scene-panel-bar"><span>tasteprint<span className="blue-text">.</span></span><span>{stages[index]} <ArrowUpRight size={12} /></span></div>
        {index === 0 && <div className="scene-choices"><span className="scene-kicker">YOUR FIRST IMPRESSION</span><h3>What looks good to you?</h3>
          {choices.slice(0, 2).map(dish => <div className="scene-choice" key={dish.id}><div className="scene-thumb"><DishImage dish={dish} eager /></div>
            <div><strong>{dish.name}</strong><span>{dish.tags.slice(0, 2).join(' · ')}</span></div>
            <span className={`scene-vote ${opinions[dish.id] === 'like' ? 'voted' : ''}`}><ThumbsUp size={15} /></span></div>)}
          <div className="scene-progress"><span /><span /><span /></div><span className="scene-footnote">A few choices. A clearer starting point.</span>
        </div>}
        {index === 1 && <div className="scene-profile"><div className="scene-profile-title"><div><span className="scene-kicker">A PROFILE, NOT A PREDICTION</span><h3>Your taste, in focus.</h3></div><Fingerprint size={37} strokeWidth={1.3} /></div>
          <div className="scene-stats"><span><strong>{summary.liked.length}</strong> liked</span><span><strong>{summary.passed.length}</strong> not for you</span></div>
          <div className="scene-patterns">{summary.patterns.length ? summary.patterns.slice(0, 3).map(pattern => <div key={pattern.tag}><span>{pattern.tag}</span><div><span style={{ width: `${pattern.count / Math.max(1, summary.liked.length) * 100}%` }} /></div><span>{pattern.count}</span></div>) : <p>Your first likes will appear here.</p>}</div>
          <span className="scene-footnote">Tags on recipes you explicitly like.</span>
        </div>}
        {index === 2 && <div className="scene-discover"><span className="scene-kicker">ILLUSTRATIVE DISCOVER PICKS</span><h3>Meet your next favourite.</h3><div className="scene-recipe-grid">{catalog.slice(3, 5).map(dish => <div key={dish.id}><div className="scene-recipe-image"><DishImage dish={dish} eager /></div><strong>{dish.name}</strong><span>{dish.tags[0]}</span></div>)}</div><span className="scene-footnote">Example picks · open Discover for live ranking</span></div>}
      </motion.div>;
    })}
    <div className="scene-seal"><Fingerprint size={22} strokeWidth={1.3} /><span>Made of<br /><strong>your choices.</strong></span></div>
  </div>;
}

function FoodGraphic() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: '100px' });
  const [pulse, setPulse] = useState(0);
  const still = <img className="food-mark-still" src="/graphics/food-mark.svg" alt="" />;
  return <div className="food-graphic" ref={ref}>
    <button type="button" className="food-mark" aria-label="Make a ripple in the food illustration" onClick={() => setPulse(value => value + 1)}>
        {inView ? <Suspense fallback={still}><RippleDistortion src="/graphics/food-mark.svg" grayscale={false} tintAmount={0} strength={0.07} swirl={0.5} rings={3} brushSize={100} fade={1.8} spread={3} pulse={pulse} trigger="hover" /></Suspense> : still}
    </button>
    <span className="graphic-caption">FOOD, WITH A LITTLE FEELING.</span>
  </div>;
}

type LandingProps = { taste: TasteState; onStart: () => void; onPick: (dish: Dish, opinion: Opinion) => void };
export default function LandingPage({ taste, onStart, onPick }: LandingProps) {
  const [phase, setPhase] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [example, setExample] = useState(true);
  const [exampleOpinions, setExampleOpinions] = useState<Record<string, Opinion>>({});
  const summary = describeTaste(taste.opinions);
  useEffect(() => {
    if (!playing) return;
    const timers = [
      window.setTimeout(() => setExampleOpinions({ [choices[0].id]: 'like' }), 900),
      window.setTimeout(() => setExampleOpinions(demoLikes), 1900),
      window.setTimeout(() => setPhase(1), 3000),
      window.setTimeout(() => setPhase(2), 5900),
      window.setTimeout(() => setPlaying(false), 7800),
    ];
    return () => timers.forEach(window.clearTimeout);
  }, [playing]);
  const watch = () => { setExample(true); setPhase(0); setExampleOpinions({}); setPlaying(true); };
  const selectPhase = (next: number) => { setPlaying(false); setPhase(next); };
  const sceneOpinions = example ? exampleOpinions : taste.opinions;
  const enter = { initial: { opacity: 0, y: 18 }, animate: { opacity: 1, y: 0 }, transition: { duration: 0.7, ease: [0.22, 1, 0.36, 1] as const } };
  return <div className="landing-page">
    <header className="landing-header"><a className="wordmark" href="#home" aria-label="Tasteprint home">tasteprint<span>.</span></a><nav aria-label="Landing navigation"><a href="#discover">Discover</a><a href="#tasteprint">Your Tasteprint</a></nav><StarBorder onClick={onStart}>Find my taste <ArrowUpRight size={15} /></StarBorder></header>
    <section className="landing-hero" aria-labelledby="landing-title">
      <div className="hero-copy"><motion.span {...enter} className="landing-eyebrow"><span /> GOOD FOOD. A LITTLE SELF-DISCOVERY.</motion.span>
        <h1 id="landing-title">{['Find your food.', 'Know your taste.'].map((text, index) => <motion.span key={text} {...enter} transition={{ ...enter.transition, delay: index * 0.15 }} className={index === 1 ? 'hero-blue' : ''}>{text}</motion.span>)}</h1>
        <motion.p {...enter} transition={{ ...enter.transition, delay: 0.3 }}>The joy of finding something delicious.<br />The little discoveries about why you love it.</motion.p>
        <motion.div {...enter} transition={{ ...enter.transition, delay: 0.4 }} className="hero-actions"><StarBorder tone="cobalt" onClick={onStart}>Find my taste <ArrowUpRight size={17} /></StarBorder>
          <button className="watch-button" type="button" onClick={playing ? () => setPlaying(false) : watch}>{playing ? <X size={15} /> : <Play size={14} fill="currentColor" />}{playing ? 'Stop preview' : 'Watch the app'}</button></motion.div>
        <p className="hero-note">A few food choices. Your own starting point.</p>
      </div>
      <div className="hero-art"><ProductScene phase={phase} opinions={sceneOpinions} /><div className="scene-controls"><span className="scene-mode">{example ? 'EXAMPLE PREVIEW' : 'YOUR SAVED CHOICES'}</span><div role="group" aria-label="App preview stage">{stages.map((stage, index) => <button type="button" key={stage} aria-pressed={phase === index} onClick={() => selectPhase(index)}><span>0{index + 1}</span>{stage}</button>)}</div></div>
        <p className="preview-description" role="status">{example ? `${playing ? 'Playing · ' : ''}${stages[phase]} · demonstration only. Example choices are never saved.` : `${summary.liked.length} liked · ${summary.passed.length} not for you · saved in this browser.`}</p></div>
    </section>
    <section className="quick-start" aria-labelledby="quick-start-title"><div className="quick-heading"><div><span className="landing-eyebrow">START WITH A GUT FEELING</span><h2 id="quick-start-title">What would you reach for?</h2></div><p>No perfect answers.<br />Just a little more you.</p></div>
      <div className="quick-grid">{choices.map(dish => <article key={dish.id} className={`quick-card ${taste.opinions[dish.id] === 'like' ? 'is-liked' : ''}`}><div className="quick-image"><DishImage dish={dish} eager /><span>{dish.tags[0]}</span>{taste.opinions[dish.id] === 'like' && <span className="quick-selected"><Check size={15} /> Liked</span>}</div>
        <div className="quick-card-body"><span className="quick-meta">{dish.category} · {formatRecipeTime(dish.totalMinutes)}</span><h3>{dish.name}</h3><OpinionButtons dish={dish} opinion={taste.opinions[dish.id]} onPick={opinion => { setPlaying(false); setExample(false); setPhase(1); onPick(dish, opinion); }} /></div></article>)}</div>
      <div className="quick-bottom"><p role="status">{Object.keys(taste.opinions).length ? <><Fingerprint size={17} /> {summary.liked.length} liked · {summary.passed.length} not for you. Your Tasteprint is taking shape.</> : <><Fingerprint size={17} /> Your choices are saved in this browser.</>}</p><button type="button" onClick={onStart} className="text-link">Continue with my taste <ArrowRight size={16} /></button></div>
    </section>
    <section className="taste-story" aria-labelledby="taste-story-label"><div className="story-copy"><span className="landing-eyebrow" id="taste-story-label">THERE’S A LITTLE STORY IN YOUR TASTE.</span><Suspense fallback={<h2 className="slow-reveal">It’s more than what’s for dinner. It’s the crunch you come back to. The comfort you crave. The little things that make a dish feel like you.</h2>}><ScrollReveal>It’s more than what’s for dinner. It’s the crunch you come back to. The comfort you crave. The little things that make a dish feel like you.</ScrollReveal></Suspense><p>Start with what you like. See what those choices have in common. Keep discovering from there.</p><a className="text-link" href="#tasteprint">A closer look at your taste <ArrowUpRight size={16} /></a></div><FoodGraphic /></section>
    <section className="landing-process" aria-labelledby="process-title"><div className="process-heading"><span className="landing-eyebrow">FROM FIRST BITE TO FIRST INSIGHT</span><h2 id="process-title">Small choices.<br /><span>A clearer picture.</span></h2></div>
      <div className="process-rows">{[
        { icon: Utensils, title: 'Trust your first impression.', text: 'Like a dish, or pass on it. A Tasteprint starts with the food you would actually reach for.', label: '01 / CHOOSE' },
        { icon: Fingerprint, title: 'See a little pattern.', text: 'Your Tasteprint counts the tags on recipes you like. An honest first sketch of your taste.', label: '02 / UNDERSTAND' },
        { icon: ArrowUpRight, title: 'Leave room for a new favourite.', text: 'Explore 5,006 real recipes in Discover. Your likes guide shared-like ranking; saves make your collection.', label: '03 / DISCOVER' },
      ].map((row, index) => <motion.article key={row.title} initial={{ opacity: 0, y: 22 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.6 }} transition={{ duration: 0.6 }}><span className="process-number">{row.label}</span><div><h3>{row.title}</h3><p>{row.text}</p></div><row.icon size={29} strokeWidth={1.3} />{index === 1 && <span className="process-tags">Fresh <span>·</span> Comforting <span>·</span> Savory</span>}</motion.article>)}</div>
    </section>
    <section className="landing-cta"><Fingerprint size={43} strokeWidth={1.1} /><h2>A good place<br />to find your taste.</h2><p>Start with a dish. See where it takes you.</p><StarBorder onClick={onStart}>Let’s find my taste <ArrowUpRight size={17} /></StarBorder><a href="#discover">Or explore the collection <ArrowRight size={14} /></a></section>
    <footer className="landing-footer"><a href="#home" className="wordmark">tasteprint<span>.</span></a><span>5,006 Food.com recipes · local demo · co-like Discover</span><a href={catalog[0].datasetUrl} target="_blank" rel="noreferrer">Recipes & attribution <ArrowUpRight size={12} /></a><button type="button" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })} aria-label="Back to top"><ArrowUp size={16} /></button></footer>
  </div>;
}
