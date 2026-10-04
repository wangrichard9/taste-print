import { afterEach, describe, expect, it, vi } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { catalog } from '../data/catalog';
import { emptyTaste } from '../lib/taste';
import { groupRequest, newGuest } from '../lib/mealmerge';
import { groupFixture } from '../test/groupFixture';
import MealMergePage from './MealMergePage';
import GroupResults from './GroupResults';
import GuestEditor from './GuestEditor';

afterEach(() => vi.unstubAllGlobals());
describe('MealMerge presentation contracts (static HTML, not interactive browser QA)', () => {
  it('shows a real local table and default policy without sample people or fixed picks', () => {
    vi.stubGlobal('localStorage', { getItem: () => null });
    const markup = renderToStaticMarkup(<MealMergePage taste={emptyTaste()} onOpenDish={() => {}} />);
    expect(markup).toContain('Guest 1'); expect(markup).toContain('Find shared recipes');
    expect(markup).toContain('Balanced compromise'); expect(markup).toContain('Overall appeal');
    expect(markup).not.toContain('Sample people'); expect(markup).not.toContain('Design preview');
    expect(markup).not.toContain('Alex'); expect(markup).not.toContain('Illustrative shortlist');
  });
  it('bounds guest browsing, identifies which person is being edited and preserves real source links', () => {
    const markup = renderToStaticMarkup(<GuestEditor guest={{ ...newGuest(), name: 'Maya' }} onRename={() => {}} onPick={() => {}} onClear={() => {}} onDone={() => {}} />);
    expect(markup.match(/class="fp-recipe"/g)).toHaveLength(12);
    expect(markup).toContain('Maya’s opinion'); expect(markup).toContain('not your Tasteprint');
    expect(markup).toContain('Original Food.com recipe'); expect(markup).toContain('All model recipes');
  });
  it('renders bounded results with honest unknown/popularity labels and no match percentages', () => {
    const request = groupRequest(emptyTaste(), [newGuest()], 'balanced');
    const markup = renderToStaticMarkup(<GroupResults result={groupFixture(request)} onOpenDish={() => {}} />);
    expect(markup.match(/class="fp-recipe mm-result-card"/g)).toHaveLength(12);
    expect(markup).toContain('Both priorities show training popularity'); expect(markup).toContain('Unknown · not a dislike');
    expect(markup).toContain('Per-person evidence'); expect(markup).not.toMatch(/\d+(?:\.\d+)?% (?:match|satisfaction)/i);
  });
  it('reports an empty eligible pool instead of inventing shared recipes', () => {
    const request = groupRequest(emptyTaste(), [newGuest()], 'balanced'); request.members[0].passes = catalog.map(dish => dish.id);
    const markup = renderToStaticMarkup(<GroupResults result={groupFixture(request)} onOpenDish={() => {}} />);
    expect(markup).toContain('No recipes remain'); expect(markup).not.toContain('mm-result-card');
  });
});
