import { describe, expect, it } from 'vitest';
import { catalog, reviewedCatalog, formatRecipeTime, onboardingDishes } from './catalog';

describe('real recipe catalog', () => {
  it('contains 30 unique source-addressable recipes, with no sample identities', () => {
    expect(reviewedCatalog).toHaveLength(30);
    expect(new Set(catalog.map(dish => dish.id)).size).toBe(5006);
    for (const dish of reviewedCatalog) {
      expect(dish.id).toBe(`foodcom:${dish.sourceRecipeId}`);
      expect(dish.sourceUrl).toMatch(new RegExp(`^https://www\\.food\\.com/recipe/.+-${dish.sourceRecipeId}$`));
      expect(dish.datasetVersion).toBe(2);
      expect(dish.image).toMatch(/^https:\/\/img\.sndimg\.com\//);
      expect(dish.ingredients.length).toBeGreaterThan(0);
      expect(dish.instructions.length).toBeGreaterThan(0);
      expect(dish.instructions.every(step => step.trim())).toBe(true);
    }
  });
  it('keeps onboarding to six starters instead of expanding to all 30', () => {
    expect(onboardingDishes).toHaveLength(6);
    expect(onboardingDishes).toEqual(reviewedCatalog.slice(0, 6));
    expect(onboardingDishes.every(dish => dish.modelSupported)).toBe(true);
  });
  it('covers every model recipe without inventing photos, directions or taste traits', () => {
    expect(catalog).toHaveLength(5006);
    expect(catalog.every(dish => dish.modelSupported)).toBe(true);
    const imported = catalog.filter(dish => !dish.manuallyReviewed);
    expect(imported).toHaveLength(4976);
    expect(catalog.filter(dish => !dish.image)).toHaveLength(60);
    expect(imported.every(dish => dish.instructions.length === 0 && dish.tags.length === 1 && dish.tags[0] === dish.category)).toBe(true);
  });
  it('formats source times without making missing times into zero minutes', () => {
    expect(formatRecipeTime(null)).toBe('Time not listed');
    expect(formatRecipeTime(0)).toBe('Time not listed');
    expect(formatRecipeTime(20)).toBe('20 min');
    expect(formatRecipeTime(60)).toBe('1 hr');
    expect(formatRecipeTime(83)).toBe('1 hr 23 min');
  });
});
