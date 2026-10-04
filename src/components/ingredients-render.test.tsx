import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { catalog, reviewedCatalog } from '../data/catalog';
import { emptyTaste } from '../lib/taste';
import type { IngredientResult } from '../lib/ingredients';
import IngredientsPage from './IngredientsPage';
import IngredientResults from './IngredientResults';

function resultFixture(): IngredientResult {
  const items = reviewedCatalog.slice(0, 16).map((dish, i) => ({ id: dish.id, knownLike: i === 15,
    basis: i === 15 ? 'known_like' as const : 'popularity' as const, matchCount: 1,
    matchedInputs: ['tomato'], matches: [{ input: 'tomato', recipeIngredient: dish.ingredients[0] }],
    additionalIngredients: dish.ingredients.slice(1) }));
  return { method: 'ingredient_rules+raw_co_like', priority: 'balanced', ingredients: ['tomato'],
    catalogSize: catalog.length, supportedLikeCount: 1, newCount: 15, knownCount: 1, items };
}

describe('Ingredients presentation contracts (static render only)', () => {
  it('offers real matching controls without fixed results or invented profile tags', () => {
    const markup = renderToStaticMarkup(<IngredientsPage taste={emptyTaste()} onOpenDish={() => {}} />);
    expect(markup).toContain('Find recipes');
    expect(markup).toContain('A little of both');
    expect(markup).toContain('This list lasts while this page is open');
    expect(markup).not.toContain('Design preview');
    expect(markup).not.toContain('sample recipes');
    expect(markup).not.toContain('Example tags');
  });
  it('bounds new cards, preserves favorites separately, and labels ingredient/taste evidence', () => {
    const markup = renderToStaticMarkup(<IngredientResults result={resultFixture()} onOpenDish={() => {}} />);
    expect(markup.match(/class="fp-recipe ingredient-recipe"/g)).toHaveLength(13);
    expect(markup).toContain('Show more new options (3 remaining)');
    expect(markup).toContain('Familiar, and still an option');
    expect(markup).toContain('You already liked this recipe');
    expect(markup).toContain('no shared-like evidence');
    expect(markup).toContain('Not allergy guidance');
    expect(markup).toContain('See ingredient matches');
  });
  it('does not fabricate recipes for a no-match result', () => {
    const result = { ...resultFixture(), newCount: 0, knownCount: 0, items: [] };
    const markup = renderToStaticMarkup(<IngredientResults result={result} onOpenDish={() => {}} />);
    expect(markup).toContain('No new recipes matched');
    expect(markup).not.toContain('ingredient-recipe');
  });
});
