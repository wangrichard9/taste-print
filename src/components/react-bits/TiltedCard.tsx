// Adapted from React Bits Tilted Card, inspected 2026-10-01.
// Copyright (c) 2026 David Haz. License: ./LICENSE.md.
// Uses children to retain Tasteprint's real image fallback and native button.
import { motion, useMotionValue, useReducedMotion, useSpring } from 'motion/react';
import { useRef, type PointerEvent, type ReactNode } from 'react';

export default function TiltedCard({ children }: { children: ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();
  const x = useMotionValue(0), y = useMotionValue(0);
  const rotateX = useSpring(x, { damping: 28, stiffness: 150, mass: .7 });
  const rotateY = useSpring(y, { damping: 28, stiffness: 150, mass: .7 });
  const scale = useSpring(1, { damping: 28, stiffness: 150 });
  const reset = () => { x.set(0); y.set(0); scale.set(1); };
  const move = (event: PointerEvent<HTMLDivElement>) => {
    if (reduced || event.pointerType !== 'mouse' || !ref.current) return;
    const bounds = ref.current.getBoundingClientRect();
    if (!bounds.width || !bounds.height) return;
    x.set(Math.max(-4, Math.min(4, -(event.clientY - bounds.top - bounds.height / 2) / (bounds.height / 2) * 4)));
    y.set(Math.max(-4, Math.min(4, (event.clientX - bounds.left - bounds.width / 2) / (bounds.width / 2) * 4)));
    scale.set(1.015);
  };
  return <div ref={ref} className="taste-tilt" onPointerMove={move} onPointerLeave={reset}
    onFocusCapture={() => { if (!reduced) scale.set(1.015); }} onBlurCapture={reset}>
    <motion.div style={{ rotateX: reduced ? 0 : rotateX, rotateY: reduced ? 0 : rotateY, scale: reduced ? 1 : scale }}>{children}</motion.div>
  </div>;
}
