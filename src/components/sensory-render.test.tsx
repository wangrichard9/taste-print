import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import TasteProfilePage from './TasteProfilePage';
import SensoryProfile from './SensoryProfile';
import { exampleTaste } from '../data/feature-previews';
import { describeSensory } from '../lib/sensory';
import { emptyTaste } from '../lib/taste';

describe('sensory profile rendering', () => {
  it('renders an empty real profile with both graphics and unknown states', () => {
    const html = renderToStaticMarkup(<TasteProfilePage taste={emptyTaste()} onEdit={() => {}} onOpenDish={() => {}} onUnsave={() => {}} />);
    expect(html).toContain('Your flavour wheel.');
    expect(html).toContain('Follow a flavour.');
    expect(html).toContain('0 of 0 liked dishes have sensory notes');
    expect(html).toContain('Unassessed');
    expect(html).not.toContain('fp-pattern-bars');
    expect(html).not.toContain('match score');
  });
  it('keeps recipe evidence from example likes visibly isolated', () => {
    const html = renderToStaticMarkup(<SensoryProfile summary={describeSensory(exampleTaste.opinions)} example onOpenDish={() => {}} />);
    expect(html).toContain('4 of 4 liked dishes have sensory notes');
    expect(html).toContain('example liked dishes');
    expect(html).toContain('View Greek salad');
    expect(html).toContain('Estimated from this recipe');
    expect(html).toContain('18 defined notes');
    expect(html).not.toContain('preference:');
  });
});
