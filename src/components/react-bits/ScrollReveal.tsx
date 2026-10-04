// Adapted from React Bits Scroll Reveal. See LICENSE.md in this directory.
import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export default function ScrollReveal({ children }: { children: string }) {
  const ref = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    if (!ref.current) return;
    const context = gsap.context(() => {
      gsap.fromTo(ref.current!.querySelectorAll('.reveal-word'), { opacity: 0.3, filter: 'blur(1px)' }, {
        opacity: 1, filter: 'blur(0px)', ease: 'none', stagger: 0.1,
        scrollTrigger: { trigger: ref.current, start: 'top 80%', end: 'bottom 32%', scrub: 0.45 },
      });
    }, ref);
    return () => context.revert();
  }, []);
  return <h2 ref={ref} className="slow-reveal" aria-label={children}><span aria-hidden="true">{children.split(/(\s+)/).map((word, index) =>
    /\s/.test(word) ? word : <span className="reveal-word" key={index}>{word}</span>)}</span></h2>;
}
