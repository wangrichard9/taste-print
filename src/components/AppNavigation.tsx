import { useEffect, useId, useRef, useState } from 'react';
import { AnimatePresence, LayoutGroup, MotionConfig, motion } from 'motion/react';
import { ArrowUpRight, Compass, Fingerprint, Carrot, Users, UserRound } from 'lucide-react';

const destinations = [
  { id: 'discover', label: 'Discover', title: 'A little possibility.', copy: 'Browse recipes. Find something you’d reach for.', icon: Compass },
  { id: 'tasteprint', label: 'Your Tasteprint', title: 'Your choices, in focus.', copy: 'Explore your taste notes, food journey and saved dishes.', icon: Fingerprint },
  { id: 'ingredients', label: 'Ingredients', title: 'Start with what you have.', copy: 'Bring a few ingredients and explore recipe options.', icon: Carrot },
  { id: 'mealmerge', label: 'MealMerge', title: 'Bring your tastes together.', copy: 'Build a local table and compare shared recipe ideas.', icon: Users },
] as const;
type Destination = typeof destinations[number]['id'];

function DestinationGraphic({ destination }: { destination: Destination }) {
  const draw = { initial: { pathLength: 0 }, animate: { pathLength: 1 }, transition: { duration: .55, ease: 'easeOut' as const } };
  return <svg className="nav-destination-graphic" viewBox="0 0 240 150" aria-hidden="true">
    {destination === 'discover' && <>
      <circle className="nav-art-faint" cx="120" cy="75" r="62" /><circle className="nav-art-faint" cx="120" cy="75" r="44" />
      {[{x:45,y:58,r:23},{x:110,y:42,r:28},{x:176,y:68,r:25},{x:110,y:111,r:21}].map((plate,index) => <motion.g key={`${plate.x}-${plate.y}`} initial={{ y: 8, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: .35, delay: index * .035 }}>
        <circle className="nav-art-disc" cx={plate.x} cy={plate.y} r={plate.r} /><circle className="nav-art-line" cx={plate.x} cy={plate.y} r={plate.r - 7} />
        <path className="nav-art-accent" d={`M ${plate.x-8} ${plate.y+2} Q ${plate.x} ${plate.y-10} ${plate.x+8} ${plate.y+2}`} />
      </motion.g>)}
    </>}
    {destination === 'tasteprint' && <>
      <circle className="nav-art-faint" cx="120" cy="75" r="54" /><circle className="nav-art-faint" cx="120" cy="75" r="35" />
      {[[43,50],[192,42],[191,113],[61,122]].map(([x,y],index) => <g key={x}>
        <motion.path {...draw} className={index === 1 ? 'nav-art-accent' : 'nav-art-line'} d={`M 120 75 Q ${x} 75 ${x} ${y}`} />
        <circle className="nav-art-disc" cx={x} cy={y} r="9" />
      </g>)}
      <circle className="nav-art-center" cx="120" cy="75" r="21" />
      <motion.path {...draw} className="nav-art-accent" d="M 111 82 C 108 68 113 61 120 61 C 131 61 133 71 127 88 M 116 87 C 118 81 114 72 120 70 C 126 70 123 80 122 86" />
    </>}
    {destination === 'ingredients' && <>
      {[34,68,102].map((y,index) => <motion.g key={y} initial={{ x: -10, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ duration: .35, delay: index * .045 }}>
        <rect className="nav-art-disc" x="25" y={y} width="81" height="23" rx="7" /><circle className="nav-art-dot" cx="39" cy={y+11.5} r="3" /><path className="nav-art-line" d={`M 49 ${y+11.5} H 91`} />
      </motion.g>)}
      <motion.path {...draw} className="nav-art-accent" d="M 115 46 C 132 46 128 79 144 79 M 115 113 C 132 113 128 79 144 79" />
      <circle className="nav-art-disc" cx="178" cy="79" r="33" /><circle className="nav-art-line" cx="178" cy="79" r="24" /><path className="nav-art-accent" d="M 166 81 Q 178 66 190 81" />
    </>}
    {destination === 'mealmerge' && <>
      {[[45,36],[45,75],[45,114]].map(([x,y],index) => <g key={y}>
        <circle className="nav-art-disc" cx={x} cy={y} r="14" /><circle className="nav-art-dot" cx={x} cy={y} r="4" />
        <motion.path {...draw} transition={{ duration: .55, delay: index * .04 }} className={index === 1 ? 'nav-art-accent' : 'nav-art-line'} d={`M 65 ${y} C 110 ${y} 110 75 152 75`} />
      </g>)}
      <circle className="nav-art-center" cx="181" cy="75" r="31" /><circle className="nav-art-line" cx="181" cy="75" r="21" /><path className="nav-art-accent" d="M 170 78 Q 181 66 192 78" />
    </>}
  </svg>;
}

export default function AppNavigation({ page }: { page: Destination }) {
  const groupId = useId();
  const previewId = useId();
  const [hovered, setHovered] = useState<Destination | null>(null);
  const [focused, setFocused] = useState<Destination | null>(null);
  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const preview = hovered ?? focused;
  const active = preview ?? page;
  const destination = destinations.find(item => item.id === preview);
  useEffect(() => { setHovered(null); setFocused(null); }, [page]);
  useEffect(() => () => { if (closeTimer.current !== null) clearTimeout(closeTimer.current); }, []);
  const cancelClose = () => { if (closeTimer.current !== null) { clearTimeout(closeTimer.current); closeTimer.current = null; } };
  const dismiss = () => { cancelClose(); setHovered(null); setFocused(null); };
  return <MotionConfig reducedMotion="never"><header className="app-header animated-app-header">
    <div className="header-inner nav-capsule" onKeyDown={event => { if (event.key === 'Escape') {
      if (preview && event.currentTarget.querySelector('.nav-destination-preview')?.contains(event.target as Node)) event.currentTarget.querySelector<HTMLAnchorElement>(`nav a[href="#${preview}"]`)?.focus();
      dismiss();
    } }} onPointerEnter={cancelClose} onPointerLeave={event => { if (event.pointerType === 'mouse') { cancelClose(); closeTimer.current = setTimeout(() => setHovered(null), 140); } }}
      onBlur={event => { if (!event.currentTarget.contains(event.relatedTarget)) setFocused(null); }}>
      <a className="wordmark" href="#home" aria-label="Tasteprint home" onClick={dismiss}>tasteprint<span>.</span></a>
      <LayoutGroup id={groupId}><nav aria-label="Main navigation">
        {destinations.map(({ id, label }) => <a key={id} href={`#${id}`} aria-current={page === id ? 'page' : undefined}
          aria-describedby={preview === id ? previewId : undefined}
          onPointerEnter={event => { if (event.pointerType === 'mouse') { cancelClose(); setHovered(id); } }}
          onFocus={() => setFocused(id)} onClick={dismiss}>
          {active === id && <motion.span className="nav-travelling-highlight" layoutId="destination-highlight" transition={{ type: 'spring', stiffness: 390, damping: 34 }} />}
          <span className="nav-destination-label">{label}</span>
        </a>)}
      </nav></LayoutGroup>
      <a className="avatar" href="#tasteprint" aria-label="Your local profile" onClick={dismiss}><UserRound size={17} aria-hidden="true" /></a>
      <AnimatePresence initial={false}>{destination && <motion.div className="nav-destination-preview" key="destination-preview" id={previewId}
        initial={{ opacity: 0, y: -6, scale: .985 }} animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -4 }} transition={{ duration: .18 }}>
        <div className="nav-preview-art"><AnimatePresence initial={false} mode="wait"><motion.div key={destination.id}
          initial={{ opacity: 0, x: 12 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -8 }} transition={{ duration: .14 }}>
          <DestinationGraphic destination={destination.id} />
        </motion.div></AnimatePresence></div>
        <div className="nav-preview-copy"><span className="eyebrow"><destination.icon size={14} aria-hidden="true" />{destination.label}</span>
          <h2>{destination.title}</h2><p>{destination.copy}</p><a className="nav-preview-hint" href={`#${destination.id}`} onClick={dismiss}>Explore {destination.label} <ArrowUpRight size={14} aria-hidden="true" /></a></div>
      </motion.div>}</AnimatePresence>
    </div>
  </header></MotionConfig>;
}
