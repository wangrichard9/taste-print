import { useEffect, useRef, useState, type PointerEvent } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'motion/react';
import { ArrowUpRight, Fingerprint, MoveUpRight } from 'lucide-react';
import type { Dish } from '../data/catalog';
import { groupLabels, sensoryGroups, type SensoryGroup, type SensoryId } from '../data/sensory';
import { type SensorySummary, type SensoryNote } from '../lib/sensory';
import DishImage from './DishImage';
import TiltedCard from './react-bits/TiltedCard';
import '../sensory.css';

function useFigureWidth() {
  const ref = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(480);
  useEffect(() => {
    if (!ref.current) return;
    const observer = new ResizeObserver(([entry]) => setWidth(Math.max(1, entry.contentRect.width)));
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);
  return { ref, width };
}

function petalPath(cx: number, cy: number, radius: number, angle: number) {
  const point = (a: number) => `${cx + Math.cos(a) * radius} ${cy + Math.sin(a) * radius}`;
  return `M ${cx} ${cy} L ${point(angle - .53)} A ${radius} ${radius} 0 0 1 ${point(angle + .53)} Z`;
}

function useDiagramExploration(selected: SensoryId) {
  const [hovered, setHovered] = useState<SensoryId | null>(null);
  const [focused, setFocused] = useState<SensoryId | null>(null);
  return {
    active: hovered ?? focused ?? selected,
    exploring: hovered !== null || focused !== null,
    bind: (id: SensoryId) => ({
      onPointerEnter: (event: PointerEvent) => { if (event.pointerType === 'mouse') setHovered(id); },
      onPointerLeave: () => setHovered(null),
      onFocus: () => setFocused(id),
      onBlur: () => setFocused(null),
    }),
    reset: () => { setHovered(null); setFocused(null); },
  };
}

function DiagramPreview({ note, id }: { note?: SensoryNote; id: string }) {
  return <div className="taste-diagram-preview" id={id}>
    {note ? <><div><strong>{note.label}</strong><span>{note.count ? `${note.count} liked ${note.count === 1 ? 'dish' : 'dishes'}` : 'Unassessed'}</span></div><p>{note.definition}</p></>
      : <p>Hover or focus a note to explore it. Select it to see the dishes behind it.</p>}
  </div>;
}

function TasteWheel({ summary, selected, onSelect }: { summary: SensorySummary; selected: SensoryId; onSelect: (id: SensoryId) => void }) {
  const { ref, width } = useFigureWidth();
  const reduced = useReducedMotion();
  const exploration = useDiagramExploration(selected);
  const notes = summary.notes.filter(note => note.group === 'taste');
  const activeNote = notes.find(note => note.id === exploration.active);
  const height = 360, cx = width / 2, cy = height / 2;
  const radius = Math.max(20, Math.min(width / 2 - 84, 116));
  return <section className="taste-wheel-panel" aria-labelledby="taste-wheel-title">
    <div className="taste-panel-heading"><span className="eyebrow">FIVE BASIC TASTES</span><span className="taste-index">01 / BALANCE</span></div>
    <h2 id="taste-wheel-title">Your flavour wheel.</h2>
    <p className="taste-panel-copy">The taste notes found in dishes you like.</p>
    <div className="taste-wheel-figure" ref={ref}>
      <svg viewBox={`0 0 ${width} ${height}`} className="taste-wheel-svg" role="img" aria-label={`Five-taste wheel. Petal radius counts liked recipes with estimated notes, out of ${summary.liked.length} likes. ${notes.map(note => `${note.label}: ${note.count ? `${note.count} dishes` : 'unassessed'}`).join('; ')}.`}>
        {[.25, .5, .75, 1].map(value => <circle key={value} cx={cx} cy={cy} r={radius * value} className="taste-wheel-grid" />)}
        {notes.map((note, index) => {
          const angle = -Math.PI / 2 + index * Math.PI * 2 / 5;
          const active = exploration.active === note.id;
          const lift = reduced ? 0 : active ? (exploration.exploring ? 6 : 3) : 0;
          return <g key={note.id} className={`taste-wheel-sector${active ? ' is-active' : ''}`}
            data-note={note.id} {...exploration.bind(note.id)}>
            <path d={petalPath(cx, cy, radius, angle)} className="taste-wheel-hit" onClick={() => onSelect(note.id)} />
            <motion.g className="taste-wheel-sector-art" animate={{ x: Math.cos(angle) * lift, y: Math.sin(angle) * lift }}
              transition={{ type: 'spring', stiffness: 320, damping: 24 }}>
            <path d={petalPath(cx, cy, radius, angle)} className="taste-wheel-sector-outline" />
            {!note.count && <path d={petalPath(cx, cy, radius, angle)} className="taste-wheel-unknown" />}
            {note.count > 0 && <motion.path className={`taste-wheel-petal${selected === note.id ? ' is-selected' : ''}`}
              initial={false} animate={{ d: petalPath(cx, cy, radius * note.count / Math.max(1, summary.liked.length), angle) }}
              transition={{ duration: reduced ? 0 : .55, ease: [.22, 1, .36, 1] }} />}
            </motion.g>
          </g>;
        })}
        <circle cx={cx} cy={cy} r={1} className="taste-wheel-center" />
      </svg>
      {notes.map((note, index) => {
        const angle = -Math.PI / 2 + index * Math.PI * 2 / 5;
        const labelRadius = radius + 44;
        return <button type="button" key={note.id} className={`taste-wheel-label${exploration.active === note.id ? ' is-explored' : ''}`} aria-pressed={selected === note.id}
          {...exploration.bind(note.id)} aria-describedby="taste-wheel-preview"
          aria-label={`Explore ${note.label}: ${note.count ? `${note.count} liked dishes` : 'not yet assessed'}`}
          style={{ left: cx + Math.cos(angle) * labelRadius, top: cy + Math.sin(angle) * labelRadius }} onClick={() => onSelect(note.id)}>
          <span>{note.label}</span><small>{note.count ? `${note.count} ${note.count === 1 ? 'dish' : 'dishes'}` : 'Unassessed'}</small>
        </button>;
      })}
    </div>
    <DiagramPreview note={activeNote} id="taste-wheel-preview" />
    <p className="taste-chart-key"><span />{summary.liked.length ? `Petal length = liked-dish count · scale 0–${summary.liked.length}` : 'Your first taste note starts with a liked dish.'}</p>
    <p className="taste-chart-note">An outline means we haven’t identified that note. It doesn’t mean you dislike it.</p>
  </section>;
}

function TasteConstellation({ summary, selected, onSelect }: { summary: SensorySummary; selected: SensoryId; onSelect: (id: SensoryId) => void }) {
  const [group, setGroup] = useState<'all' | SensoryGroup>('all');
  const { ref, width } = useFigureWidth();
  const reduced = useReducedMotion();
  const exploration = useDiagramExploration(selected);
  const starterIds: SensoryId[] = ['herby', 'citrusy', 'creamy', 'crunchy', 'roasted', 'chili_hot'];
  const candidates = summary.notes.filter(note => group === 'all' || note.group === group)
    .sort((a, b) => b.count - a.count || (!summary.annotatedCount && group === 'all'
      ? (starterIds.includes(a.id) ? starterIds.indexOf(a.id) : 99) - (starterIds.includes(b.id) ? starterIds.indexOf(b.id) : 99)
      : a.label.localeCompare(b.label)));
  const visible = candidates.slice(0, 6);
  const picked = candidates.find(note => note.id === selected);
  if (picked && !visible.some(note => note.id === selected)) visible[visible.length - 1] = picked;
  const positions = [[.5, .1], [.82, .31], [.78, .77], [.5, .94], [.22, .77], [.18, .31]];
  const points = visible.map((_, index) => ({ x: Math.max(79, Math.min(width - 79, width * positions[index][0])), y: 350 * positions[index][1] }));
  const cx = width / 2, cy = 166;
  const activeIndex = visible.findIndex(note => note.id === exploration.active);
  const activeNote = visible[activeIndex];
  const activePoint = points[activeIndex];
  return <section className="taste-constellation-panel" aria-labelledby="taste-constellation-title">
    <div className="taste-panel-heading"><span className="eyebrow">YOUR TASTE CONSTELLATION</span><span className="taste-index">02 / CHARACTER</span></div>
    <h2 id="taste-constellation-title">Follow a flavour.</h2>
    <div className="taste-group-controls" role="group" aria-label="Constellation vocabulary group">
      {(['all', ...sensoryGroups] as const).map(id => <button type="button" key={id} aria-pressed={group === id} onClick={() => { exploration.reset(); setGroup(id); }}>{id === 'all' ? 'All notes' : groupLabels[id]}</button>)}
    </div>
    <div className="taste-constellation-figure" ref={ref}>
      <svg viewBox={`0 0 ${width} 350`} className="taste-constellation-lines" aria-hidden="true">
        <circle cx={cx} cy={cy} r={90} className="taste-orbit" />
        <circle cx={cx} cy={cy} r={119} className="taste-orbit" />
        {visible.map((note, index) => <motion.path key={note.id} className={`taste-link${selected === note.id ? ' is-selected' : ''}${exploration.active === note.id ? ' is-explored' : ''}`}
          d={`M ${cx} ${cy} Q ${points[index].x} ${cy} ${points[index].x} ${points[index].y}`}
          initial={{ pathLength: reduced ? 1 : 0 }} animate={{ pathLength: 1 }} transition={{ duration: reduced ? 0 : .7, delay: reduced ? 0 : index * .045 }} />)}
        {exploration.exploring && activePoint && !reduced && <g key={exploration.active}>
          <motion.circle className="taste-connection-dot" r={3.5}
            initial={{ opacity: 0 }} animate={{ cx: [cx, .25 * cx + .75 * activePoint.x, activePoint.x], cy: [cy, .75 * cy + .25 * activePoint.y, activePoint.y], opacity: [0, 1, 0] }}
            transition={{ duration: .65, ease: 'easeOut' }} />
          <motion.circle className="taste-connection-ripple" cx={cx} cy={cy} initial={{ r: 44, opacity: .3 }} animate={{ r: 73, opacity: 0 }} transition={{ duration: .7 }} />
        </g>}
      </svg>
      <motion.div className="taste-constellation-center" animate={{ scale: exploration.exploring && !reduced ? 1.035 : 1 }} transition={{ duration: .2 }}><Fingerprint size={44} strokeWidth={1} aria-hidden="true" /><span>Your choices</span></motion.div>
      {visible.map((note, index) => <motion.button type="button" key={note.id} className={`taste-node${note.count ? '' : ' is-unassessed'}`}
        style={{ left: points[index].x, top: points[index].y }} aria-pressed={selected === note.id}
        {...exploration.bind(note.id)} aria-describedby="taste-constellation-preview"
        initial={{ opacity: reduced ? 1 : 0 }} animate={{ opacity: 1 }} transition={{ duration: .2 }}
        whileHover={reduced ? undefined : { scale: 1.07, y: -3 }} whileFocus={reduced ? undefined : { scale: 1.07, y: -3 }} whileTap={reduced ? undefined : { scale: .97 }}
        aria-label={`Explore ${note.label}: ${note.count ? `${note.count} liked dishes` : 'not yet assessed'}`} onClick={() => onSelect(note.id)}>
        <span>{note.label}</span><small>{note.count ? note.count.toString().padStart(2, '0') : '—'}</small>
      </motion.button>)}
    </div>
    <DiagramPreview note={activeNote} id="taste-constellation-preview" />
    <p className="taste-chart-note">Select a word to see what it means and the dishes behind it. Connections show your choices, not similarity scores.</p>
  </section>;
}

function NoteEvidence({ note, example, onOpenDish }: { note: SensoryNote; example: boolean; onOpenDish: (dish: Dish, previewOnly?: boolean) => void }) {
  const [expanded, setExpanded] = useState(false);
  const reduced = useReducedMotion();
  const entries = note.evidence.slice(0, expanded ? undefined : 4);
  return <motion.section className="taste-evidence" initial={{ opacity: reduced ? 1 : 0, y: reduced ? 0 : 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: reduced ? 1 : 0, y: reduced ? 0 : -5 }} transition={{ duration: reduced ? 0 : .2 }} aria-labelledby="taste-evidence-title">
    <div className="taste-definition" aria-live="polite"><span className="eyebrow">{groupLabels[note.group]} / SELECTED NOTE</span>
      <h2 id="taste-evidence-title">{note.label}<span>{note.count ? note.count.toString().padStart(2, '0') : '—'}</span></h2>
      <p>{note.definition}</p><span className="taste-evidence-label">{note.count ? `Appears in ${note.count} ${example ? 'example ' : ''}liked ${note.count === 1 ? 'dish' : 'dishes'}.` : 'No supported recipe notes yet. This is unknown, not a dislike.'}</span>
    </div>
    <div className="taste-evidence-recipes">
      {entries.map(({ dish, reason }) => <article className="taste-evidence-recipe" key={dish.id}>
        <TiltedCard><button type="button" className="taste-evidence-image" onClick={() => onOpenDish(dish, example)} aria-label={`View ${dish.name}`}><DishImage dish={dish} /><ArrowUpRight size={20} aria-hidden="true" /></button></TiltedCard>
        <div><button type="button" className="taste-recipe-title" onClick={() => onOpenDish(dish, example)}>{dish.name}</button><p>{reason}</p><small>Estimated from this recipe</small></div>
      </article>)}
      {!entries.length && <div className="taste-unassessed"><Fingerprint size={28} strokeWidth={1.2} aria-hidden="true" /><h3>Room for another note.</h3><p>Keep choosing dishes. This graphic only grows when a liked recipe has a supported note.</p></div>}
      {note.count > 4 && <button type="button" className="text-link" aria-expanded={expanded} onClick={() => setExpanded(value => !value)}>{expanded ? 'Show fewer dishes' : `See all ${note.count} dishes`} <MoveUpRight size={15} aria-hidden="true" /></button>}
    </div>
  </motion.section>;
}

export default function SensoryProfile({ summary, example, onOpenDish }: { summary: SensorySummary; example: boolean; onOpenDish: (dish: Dish, previewOnly?: boolean) => void }) {
  const [selected, setSelected] = useState<SensoryId>(() => summary.annotatedCount ? [...summary.notes].sort((a, b) => b.count - a.count)[0].id : 'herby');
  const selectedNote = summary.notes.find(note => note.id === selected)!;
  return <div className="sensory-profile">
    <div className="taste-coverage"><span><Fingerprint size={16} aria-hidden="true" />{summary.annotatedCount} of {summary.liked.length} liked dishes have sensory notes</span><p>Authored estimates from recipe ingredients and methods.</p></div>
    {summary.unannotatedCount > 0 && <p className="taste-coverage-gap">{summary.unannotatedCount} liked {summary.unannotatedCount === 1 ? 'recipe is' : 'recipes are'} still unassessed. Those likes continue to inform recommendations.</p>}
    <div className="taste-graphics">
      <TasteWheel summary={summary} selected={selected} onSelect={setSelected} />
      <TasteConstellation summary={summary} selected={selected} onSelect={setSelected} />
    </div>
    <AnimatePresence mode="wait" initial={false}><NoteEvidence key={selected} note={selectedNote} example={example} onOpenDish={onOpenDish} /></AnimatePresence>
    <details className="taste-dictionary"><summary>The vocabulary behind your Tasteprint <span>18 defined notes</span></summary>
      <div className="taste-dictionary-groups">{sensoryGroups.map(group => <section key={group}><h3>{groupLabels[group]}</h3>{summary.notes.filter(note => note.group === group).map(note => <div key={note.id}><button type="button" aria-pressed={selected === note.id} onClick={() => setSelected(note.id)}>{note.label}<span>{note.count || '—'}</span></button><p>{note.definition}</p></div>)}</section>)}</div>
      <p className="evidence-note">sensory-v1 · A controlled Tasteprint vocabulary, not a measured sensory test. Unlisted notes are unassessed. Counts describe liked dishes, not the reason you liked them.</p>
    </details>
  </div>;
}
