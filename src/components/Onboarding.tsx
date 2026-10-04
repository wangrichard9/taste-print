import { useState } from 'react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import { onboardingDishes, type Dish } from '../data/catalog';
import { describeTaste, setOpinion, type Opinion, type TasteState } from '../lib/taste';
import Dialog from './Dialog';
import DishImage from './DishImage';
import Stepper from './react-bits/Stepper';

export function OpinionButtons({ dish, opinion, onPick, personName }: {
  dish: Dish; opinion?: Opinion; onPick: (opinion: Opinion) => void; personName?: string;
}) {
  return <div className="opinion-buttons" role="group" aria-label={`${personName ? `${personName}’s` : 'Your'} opinion of ${dish.name}`}>
    <button type="button" aria-pressed={opinion === 'like'} aria-label={`Like ${dish.name}${personName ? ` for ${personName}` : ''}`} onClick={() => onPick('like')}>
      <ThumbsUp size={15} aria-hidden="true" /> Like it
    </button>
    <button type="button" aria-pressed={opinion === 'pass'} aria-label={`Pass on ${dish.name}${personName ? ` for ${personName}` : ''}`} onClick={() => onPick('pass')}>
      <ThumbsDown size={15} aria-hidden="true" /> {personName ? 'Pass' : 'Not for me'}
    </button>
  </div>;
}

export default function Onboarding({ taste, onClose, onComplete }: {
  taste: TasteState; onClose: () => void; onComplete: (opinions: Record<string, Opinion>) => void;
}) {
  const [draft, setDraft] = useState({ ...taste.opinions });
  const summary = describeTaste(draft);
  const count = summary.liked.length + summary.passed.length;
  const pick = (id: string, opinion: Opinion) => setDraft(previous => setOpinion({ ...taste, opinions: previous }, id, opinion).opinions);
  const choices = (dishes: Dish[], title: string, subtitle: string) => <section>
    <h2 data-step-heading tabIndex={-1}>{title}</h2>
    <p className="step-description">{subtitle} You can leave a dish undecided.</p>
    <div className="choice-grid">{dishes.map(dish => <article className="choice-card" key={dish.id}>
      <div className="choice-image"><DishImage dish={dish} eager /></div>
      <h3>{dish.name}</h3><p>{dish.tags.slice(0, 2).join(' · ')}</p>
      <OpinionButtons dish={dish} opinion={draft[dish.id]} onPick={opinion => pick(dish.id, opinion)} />
    </article>)}</div>
  </section>;
  return <Dialog titleId="onboarding-title" onClose={onClose} wide>
    <div className="onboarding-heading"><span className="eyebrow">YOUR TASTE, IN FOCUS</span>
      <h1 id="onboarding-title">Start with what you <span>love.</span></h1>
      <p>Six real recipes. No right answers. Just a starting point.</p>
    </div>
    <Stepper labels={['First impressions', 'A little variety', 'Your choices']} canComplete={count >= 2}
      onFinalStepCompleted={() => onComplete(draft)}>
      {choices(onboardingDishes.slice(0, 3), 'What catches your eye?', 'Choose the dishes you would reach for.')}
      {choices(onboardingDishes.slice(3, 6), 'And what about these?', 'A few different flavours and textures.')}
      <section className="choice-review">
        <h2 data-step-heading tabIndex={-1}>A first sketch of your taste.</h2>
        <p className="step-description">{count >= 2 ? 'Ready to apply your choices. You can change them any time.' : 'Go back and give at least two dishes an opinion to get started.'}</p>
        <div className="review-counts"><div><strong>{summary.liked.length}</strong><span>Dishes you like</span></div>
          <div><strong>{summary.passed.length}</strong><span>Not for you</span></div><div><strong>{onboardingDishes.filter(dish => !draft[dish.id]).length}</strong><span>Starter choices open</span></div></div>
        <div className="review-list">{[...summary.liked, ...summary.passed].map(dish => <div key={dish.id}>
          <span>{dish.name}</span><span className={draft[dish.id] === 'like' ? 'blue-text' : ''}>{draft[dish.id] === 'like' ? 'Like it' : 'Not for me'}</span>
        </div>)}</div>
        <p className="evidence-note">These are your explicit choices, not learned taste traits. All six starters are supported by the co-like model; they are an editorial selection, not an optimized onboarding strategy. Likes rank new dishes in Discover; passes exclude that dish, not its ingredients. Other recorded opinions remain in this review.</p>
      </section>
    </Stepper>
    <p className="dialog-footnote">Changes apply only when you finish. Saved in this browser; recipe choices are used by the local model on this computer. No account or cloud profile.</p>
  </Dialog>;
}
