import recipes from './recipes.json';
import modelRecipes from './model-recipes.json';

export type Dish = {
  id: string;
  sourceRecipeId: number;
  sourceName: string;
  sourceCategory: string | null;
  sourceUrl: string;
  datasetUrl: string;
  datasetVersion: number;
  name: string;
  category: string;
  description: string;
  image: string;
  imageAlt: string;
  imageSource: string;
  tags: string[];
  ingredients: string[];
  instructions: string[];
  totalMinutes: number | null;
  servings: number | null;
  modelSupported?: boolean;
  manuallyReviewed?: boolean;
};

// Real version-2 metadata; display names, descriptions and taste tags are editorial.
// Ingredient metadata is not verified amounts or allergen safety.
export const reviewedCatalog: Dish[] = recipes.map(dish => ({ ...dish, modelSupported: true, manuallyReviewed: true }));
export const catalog: Dish[] = [...reviewedCatalog, ...modelRecipes];
export const dishById = new Map(catalog.map(dish => [dish.id, dish]));
export const onboardingDishes = reviewedCatalog.filter(dish => dish.modelSupported).slice(0, 6);

export function formatRecipeTime(minutes: number | null): string {
  if (minutes === null || minutes <= 0) return 'Time not listed';
  const rounded = Math.ceil(minutes);
  return rounded < 60 ? `${rounded} min` : `${Math.floor(rounded / 60)} hr${rounded % 60 ? ` ${rounded % 60} min` : ''}`;
}
