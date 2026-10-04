import { afterEach, describe, expect, it, vi } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import App from '../App';
import { catalog, reviewedCatalog } from '../data/catalog';
import DishImage from './DishImage';
import SourceDirections from './SourceDirections';

afterEach(() => vi.unstubAllGlobals());

describe('Discover presentation contracts (static render, not browser verification)', () => {
  it('bounds initial card rendering and truthfully identifies loading and sample features', () => {
    // Motion's shared layout indicator registers resize listeners on the window.
    vi.stubGlobal('window', { location: { hash: '#discover' }, addEventListener: vi.fn(), removeEventListener: vi.fn() });
    vi.stubGlobal('localStorage', { getItem: () => null });
    const markup = renderToStaticMarkup(<App />);
    expect(markup.match(/class="dish-card"/g)).toHaveLength(24);
    expect(markup).toContain('Connecting your choices to the local model');
    expect(markup).toContain('Refresh recommendations');
    expect(markup).toContain('Refreshing');
    expect(markup).toContain('5,006');
    expect(markup).toContain('local co-like Discover, Ingredients &amp; MealMerge');
    expect(markup).not.toContain('no recommendation engine connected');
  });
  it('renders a real missing-photo fallback without an empty image source', () => {
    const missing = catalog.find(dish => !dish.image)!;
    const markup = renderToStaticMarkup(<DishImage dish={missing} />);
    expect(markup).toContain('Photo unavailable');
    expect(markup).not.toContain('<img');
  });
  it('preserves reviewed steps and labels on-demand directions as loading', () => {
    const reviewed = renderToStaticMarkup(<SourceDirections dish={reviewedCatalog[0]} />);
    expect(reviewed).toContain('recipe-directions');
    const imported = catalog.find(dish => !dish.manuallyReviewed)!;
    expect(renderToStaticMarkup(<SourceDirections dish={imported} />)).toContain('Loading source directions');
  });
});
