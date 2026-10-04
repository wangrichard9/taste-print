// Adapted from React Bits Star Border. See LICENSE.md in this directory.
import type { ComponentPropsWithoutRef, ReactNode } from 'react';

type Shared = { children: ReactNode; className?: string; tone?: 'cobalt' | 'white' };
type Props = Shared & ({ as: 'a' } & ComponentPropsWithoutRef<'a'> | { as?: 'button' } & ComponentPropsWithoutRef<'button'>);

export default function StarBorder(props: Props) {
  const content = <><span className="star-trail star-top" aria-hidden="true" /><span className="star-trail star-bottom" aria-hidden="true" /><span className="star-content">{props.children}</span></>;
  if (props.as === 'a') {
    const { as, children, className = '', tone = 'white', ...rest } = props;
    void as; void children;
    return <a {...rest} className={`star-border star-${tone} ${className}`}>{content}</a>;
  }
  const { as, children, className = '', tone = 'white', ...rest } = props;
  void as; void children;
  return <button type="button" {...rest} className={`star-border star-${tone} ${className}`}>{content}</button>;
}
