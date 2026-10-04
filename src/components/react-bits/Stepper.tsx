/**
 * Adapted from David Haz's React Bits TypeScript Stepper (2026-09-30).
 * https://github.com/DavidHDev/react-bits/blob/main/src/ts-default/Components/Stepper/Stepper.tsx
 * Copyright (c) 2026 David Haz. MIT + Commons Clause; see ./LICENSE.md.
 * Changes: scoped styling, keyboard buttons, backward-only indicators, bounded
 * motion, reduced-motion support, resize-aware content, final-step validation.
 */
import { AnimatePresence, motion, useReducedMotion, type Variants } from 'motion/react';
import { Children, Fragment, useCallback, useLayoutEffect, useRef, useState, type ReactNode } from 'react';

type StepperProps = {
  children: ReactNode;
  labels: string[];
  onStepChange?: (step: number) => void;
  onFinalStepCompleted: () => void;
  canComplete: boolean;
};

export default function Stepper({ children, labels, onStepChange, onFinalStepCompleted, canComplete }: StepperProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [direction, setDirection] = useState(0);
  const stepsArray = Children.toArray(children);
  const isLastStep = currentStep === stepsArray.length;
  const reduced = useReducedMotion();
  const updateStep = (next: number) => {
    setDirection(next > currentStep ? 1 : -1);
    setCurrentStep(next);
    onStepChange?.(next);
  };
  return <div className="rb-stepper">
    <div className="rb-indicators" aria-label="Preference setup progress">
      {stepsArray.map((_, index) => {
        const step = index + 1;
        return <Fragment key={step}>
          <button type="button" className="rb-indicator" aria-current={currentStep === step ? 'step' : undefined}
            disabled={step >= currentStep} onClick={() => updateStep(step)}
            aria-label={`Step ${step}: ${labels[index]}${step < currentStep ? ', go back' : ''}`}>
            <motion.span className={`rb-circle ${currentStep >= step ? 'is-active' : ''}`} initial={false}
              animate={{ backgroundColor: currentStep >= step ? '#2647eb' : '#f2f4f8' }}
              transition={{ duration: reduced ? 0 : 0.18 }}>
              {currentStep > step ? <CheckIcon /> : step}
            </motion.span>
            <span>{labels[index]}</span>
          </button>
          {index < stepsArray.length - 1 && <div className="rb-connector" aria-hidden="true">
            <motion.div initial={false} animate={{ width: currentStep > step ? '100%' : 0 }}
              transition={{ duration: reduced ? 0 : 0.2 }} />
          </div>}
        </Fragment>;
      })}
    </div>
    <StepContentWrapper currentStep={currentStep} direction={direction}>{stepsArray[currentStep - 1]}</StepContentWrapper>
    <div className="rb-footer">
      {currentStep > 1 ? <button type="button" className="button secondary" onClick={() => updateStep(currentStep - 1)}>Back</button> : <span />}
      <button type="button" className="button primary" disabled={isLastStep && !canComplete}
        onClick={() => { if (isLastStep) { if (canComplete) onFinalStepCompleted(); } else updateStep(currentStep + 1); }}>
        {isLastStep ? 'Apply my choices' : 'Continue'}
      </button>
    </div>
  </div>;
}

function StepContentWrapper({ currentStep, direction, children }: { currentStep: number; direction: number; children: ReactNode }) {
  const [parentHeight, setParentHeight] = useState<number>();
  const measure = useCallback((height: number) => setParentHeight(height), []);
  const reduced = useReducedMotion();
  return <motion.div className="rb-content" animate={{ height: parentHeight }} transition={{ duration: reduced ? 0 : 0.2 }}>
    <AnimatePresence initial={false} mode="wait" custom={direction}>
      <SlideTransition key={currentStep} direction={direction} onHeightReady={measure}>{children}</SlideTransition>
    </AnimatePresence>
  </motion.div>;
}

const stepVariants: Variants = {
  enter: (direction: number) => ({ x: direction >= 0 ? 16 : -16, opacity: 0 }),
  center: { x: 0, opacity: 1 },
  exit: (direction: number) => ({ x: direction >= 0 ? -16 : 16, opacity: 0 }),
};

function SlideTransition({ children, direction, onHeightReady }: { children: ReactNode; direction: number; onHeightReady: (height: number) => void }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();
  useLayoutEffect(() => {
    const element = containerRef.current;
    if (!element) return;
    const update = () => onHeightReady(element.offsetHeight);
    update();
    const observer = new ResizeObserver(update);
    observer.observe(element);
    const heading = element.querySelector<HTMLElement>('[data-step-heading]');
    heading?.focus({ preventScroll: true });
    return () => observer.disconnect();
  }, [onHeightReady]);
  return <motion.div ref={containerRef} custom={direction} variants={reduced ? undefined : stepVariants}
    initial={reduced ? false : 'enter'} animate="center" exit="exit" transition={{ duration: reduced ? 0 : 0.18 }}>
    {children}
  </motion.div>;
}

function CheckIcon() {
  const reduced = useReducedMotion();
  return <svg aria-hidden="true" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
    <motion.path initial={{ pathLength: reduced ? 1 : 0 }} animate={{ pathLength: 1 }}
      transition={{ duration: reduced ? 0 : 0.2 }} strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
  </svg>;
}
