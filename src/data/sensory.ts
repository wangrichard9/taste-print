export const sensoryVersion = 'sensory-v1';
export const sensoryGroups = ['taste', 'aroma', 'texture', 'sensation'] as const;
export type SensoryGroup = typeof sensoryGroups[number];

// Controlled app vocabulary, grounded in sensory distinctions, not a validated
// preference instrument. Definitions and recipe estimates are independently versioned.
export const sensoryVocabulary = [
  { id: 'sweet', label: 'Sweet', group: 'taste', definition: 'Perceived sweetness, rather than the mere presence of sugar.', aliases: [] },
  { id: 'sour', label: 'Sour', group: 'taste', definition: 'A tart, acidic taste. Tangy is our everyday synonym.', aliases: ['Tangy'] },
  { id: 'salty', label: 'Salty', group: 'taste', definition: 'A noticeable salty note, not simply salt listed in a recipe.', aliases: [] },
  { id: 'bitter', label: 'Bitter', group: 'taste', definition: 'A distinctly bitter taste, separate from sourness or chili heat.', aliases: [] },
  { id: 'umami', label: 'Umami', group: 'taste', definition: 'Glutamate-like savory taste, as in mushrooms, aged cheese or broth.', aliases: ['Savory, when used specifically for umami'] },
  { id: 'herby', label: 'Herby', group: 'aroma', definition: 'Recognizable herb aromas, such as basil, parsley or rosemary.', aliases: [] },
  { id: 'citrusy', label: 'Citrusy', group: 'aroma', definition: 'Lemon, lime or other citrus aromas. Distinct from acidic taste.', aliases: [] },
  { id: 'fruity', label: 'Fruity', group: 'aroma', definition: 'Recognizable fruit aromas other than our separately tracked citrus family.', aliases: [] },
  { id: 'smoky', label: 'Smoky', group: 'aroma', definition: 'A smoke-like aroma. Grilling alone does not establish this note.', aliases: [] },
  { id: 'roasted', label: 'Roasted', group: 'aroma', definition: 'Toasted or browned aromas supported by the preparation method.', aliases: ['Toasty'] },
  { id: 'nutty', label: 'Nutty', group: 'aroma', definition: 'Nut-like aromas; the description does not guarantee nut ingredients.', aliases: [] },
  { id: 'warm_spiced', label: 'Warm-spiced', group: 'aroma', definition: 'Cinnamon, clove or similar warm spice aromas, separate from chili burn.', aliases: [] },
  { id: 'creamy', label: 'Creamy', group: 'texture', definition: 'A smooth, creamy mouthfeel supported by the recipe preparation.', aliases: [] },
  { id: 'crunchy', label: 'Crunchy', group: 'texture', definition: 'A noticeable crisp or brittle bite, such as raw cucumber or croutons.', aliases: ['Crisp, when describing a crunchy bite'] },
  { id: 'chewy', label: 'Chewy', group: 'texture', definition: 'Sustained resistance while chewing, beyond simply firm or tender.', aliases: [] },
  { id: 'tender', label: 'Tender', group: 'texture', definition: 'An easily yielding bite supported by the preparation instructions.', aliases: [] },
  { id: 'chili_hot', label: 'Chili-hot', group: 'sensation', definition: 'Chili-like burn or pungency, separate from serving temperature.', aliases: [] },
  { id: 'cooling', label: 'Cooling', group: 'sensation', definition: 'Mint-like chemical cooling, separate from a dish being served cold.', aliases: [] },
] as const;

export type SensoryId = typeof sensoryVocabulary[number]['id'];
export type SensoryTerm = typeof sensoryVocabulary[number];
export const basicTastes = sensoryVocabulary.filter(term => term.group === 'taste');
export const sensoryById = new Map<SensoryId, SensoryTerm>(sensoryVocabulary.map(term => [term.id, term]));
export const groupLabels: Record<SensoryGroup, string> = { taste: 'Basic tastes', aroma: 'Aromas', texture: 'Textures', sensation: 'Heat & cooling' };

export type RecipeSensoryAnnotation = { version: typeof sensoryVersion; basis: 'metadata-estimate'; notes: Partial<Record<SensoryId, string>> };
const estimate = (notes: RecipeSensoryAnnotation['notes']): RecipeSensoryAnnotation => ({ version: sensoryVersion, basis: 'metadata-estimate', notes });

// Explicit, authored positive estimates for the 30 reviewed recipes. Evidence is
// read from their ingredients/instructions, not old editorial tags or the model.
// An omitted term is UNASSESSED, never a measured absence or intensity of zero.
export const recipeSensoryNotes: Record<string, RecipeSensoryAnnotation> = {
  'foodcom:90975': estimate({ sour: 'Lemon juice and red wine vinegar in the salad dressing.', salty: 'Feta and kalamata olives supply a plausible salty note.', herby: 'Oregano in the dressing.', citrusy: 'Lemon juice in the dressing.', crunchy: 'Raw cucumber, lettuce and peppers in the salad.' }),
  'foodcom:28199': estimate({ herby: 'Basil and fresh parsley season the baked salmon.', citrusy: 'Lemon juice seasons the salmon.', sour: 'Lemon juice in the marinade suggests a tart note.' }),
  'foodcom:29301': estimate({ chili_hot: 'Cayenne pepper is part of the chicken seasoning.', fruity: 'Golden raisins are cooked into the curry.', creamy: 'Yogurt is stirred into the sauce.', umami: 'Chicken broth and tomato paste form the sauce base.', herby: 'Fresh cilantro in the curry.' }),
  'foodcom:91318': estimate({ sour: 'Lemon juice in the pasta salad dressing.', citrusy: 'Lemon juice in the dressing.', herby: 'Cilantro in the pasta salad.', crunchy: 'Raw peppers and onion are mixed into the salad.', umami: 'Cheddar adds a plausible aged-cheese savory note.' }),
  'foodcom:94673': estimate({ herby: 'Fresh cilantro in the lentil soup.', citrusy: 'Fresh lemon juice in the soup.', sour: 'Lemon juice provides a plausible tart note.', creamy: 'Blending cooked lentils suggests a creamy texture; the instructions allow a chunkier result.' }),
  'foodcom:60350': estimate({ umami: 'Cheddar is melted into the cheese sauce.', creamy: 'Milk, butter and flour are cooked into a smooth cheese sauce.' }),
  'foodcom:304604': estimate({ umami: 'Beef bouillon is cooked into the lentils.', tender: 'The lentils and rice simmer until cooked.' }),
  'foodcom:95383': estimate({ herby: 'Oregano and basil season the chicken and zucchini.', citrusy: 'Fresh lemon juice in the sauce.', sour: 'Lemon juice in the sauce suggests tartness.', umami: 'Chicken broth is part of the sauce.' }),
  'foodcom:81968': estimate({ herby: 'Oregano seasons the chickpeas and spinach.', citrusy: 'Lemon is used in the dish.', chili_hot: 'Red pepper flakes season the chickpeas.', tender: 'Chickpeas and spinach are cooked together until tender.' }),
  'foodcom:213535': estimate({ umami: 'Mushrooms, parmesan and chicken broth in the risotto.', creamy: 'Arborio rice is stirred with broth and finished with butter and parmesan.', herby: 'Chives in the finished risotto.' }),
  'foodcom:131639': estimate({ roasted: 'The tomatoes and garlic are roasted before making the soup.', herby: 'Oregano and basil in the soup.', umami: 'Tomatoes, parmesan and chicken broth in the soup.', creamy: 'The roasted vegetables are blended into soup.' }),
  'foodcom:266209': estimate({ herby: 'Fresh parsley in the meatball mixture.', roasted: 'Frying the meatballs in oil suggests browned aromas; the source does not measure them.' }),
  'foodcom:22910': estimate({ umami: 'Soy sauce seasons the fried rice.', salty: 'Soy sauce supplies a plausible salty note.', tender: 'Cooked rice and scrambled egg form the dish.' }),
  'foodcom:129926': estimate({ creamy: 'A sour-cream sauce is poured over the enchiladas.', chili_hot: 'Fresh chili peppers and green chilies in the filling and sauce.', umami: 'Monterey jack cheese and chicken broth in the dish.' }),
  'foodcom:115954': estimate({ citrusy: 'Lemon juice in the salmon marinade.', sour: 'The lemon marinade suggests a tart note.', roasted: 'Salmon is cooked on the grill; browned aroma is estimated, not smoke.' }),
  'foodcom:79308': estimate({ umami: 'Stewed tomatoes and tomato paste form the chili base.', herby: 'Oregano in the chili.', tender: 'Turkey and beans simmer in the sauce.' }),
  'foodcom:106251': estimate({ roasted: 'The instructions roast until browned.', herby: 'Fresh rosemary seasons the cauliflower.', tender: 'Roasting softens the cauliflower.' }),
  'foodcom:47640': estimate({ herby: 'Basil and oregano in the soup.', umami: 'Broth and tomato paste form the soup base.', tender: 'The instructions simmer until the vegetables are tender.' }),
  'foodcom:30165': estimate({ umami: 'Cheddar and sausage in the burrito filling.', chili_hot: 'Green chilies in the filling suggest chili heat; strength is unknown.' }),
  'foodcom:153569': estimate({ sour: 'Lemon juice and Dijon mustard in the dressing.', citrusy: 'Lemon juice in the dressing.', umami: 'Anchovy paste and parmesan in the salad.', salty: 'Anchovy paste and parmesan suggest a salty note.', crunchy: 'Romaine and croutons are mixed into the salad.' }),
  'foodcom:749': estimate({ umami: 'Tomato paste, beef and cheeses form the lasagna layers.', herby: 'Oregano, basil and thyme season the sauce.', tender: 'The instructions cook zucchini until tender before baking.' }),
  'foodcom:43469': estimate({ sweet: 'Sweet potato is the main ingredient, with cinnamon seasoning.', warm_spiced: 'Cinnamon seasons the sweet potatoes.', roasted: 'The instructions bake until browned on the outside.', tender: 'The instructions specify a soft interior.' }),
  'foodcom:46221': estimate({ herby: 'Oregano in the beans.', sour: 'Cider vinegar is cooked into the sauce.', tender: 'The beans simmer and some are mashed into the sauce.' }),
  'foodcom:11808': estimate({ umami: 'Mushrooms and parmesan in the linguine sauce.', herby: 'Basil and parsley in the sauce.', roasted: 'The instructions brown garlic before adding mushrooms.' }),
  'foodcom:86112': estimate({ umami: 'Mushrooms and parmesan in the frittata.', roasted: 'The instructions broil until the cheese is lightly browned.' }),
  'foodcom:322833': estimate({ sour: 'Lime juice in the dressing.', citrusy: 'Lime juice in the dressing.', herby: 'Cilantro in the dressing.', crunchy: 'Raw cucumber and onion are mixed with cooked pasta.' }),
  'foodcom:25360': estimate({ tender: 'The cooked chickpeas simmer with the sauce.', umami: 'Tomatoes are cooked into the chickpea sauce.' }),
  'foodcom:120810': estimate({ nutty: 'Finely ground cashews are cooked into the sauce.', creamy: 'Cashews and yogurt thicken the sauce.', chili_hot: 'Cayenne is cooked with the spices.', herby: 'Fresh cilantro in the curry.', umami: 'Tomatoes in the chicken sauce.' }),
  'foodcom:76470': estimate({ citrusy: 'Fresh lime is squeezed into the skillet.', sour: 'Lime juice suggests a tart note.', chili_hot: 'Cayenne in the seasoning blend.', herby: 'Parsley and thyme in the seasoning blend.', roasted: 'The instructions sauté shrimp until they begin to brown.' }),
  'foodcom:133563': estimate({ herby: 'Rosemary is cooked in and used as garnish.', creamy: 'The instructions puree the soup until smooth.', citrusy: 'Lemon juice is stirred in after blending.', sour: 'Lemon juice added at the end suggests tartness.', chili_hot: 'Crushed red pepper flakes are cooked with garlic and rosemary.', umami: 'Chicken broth forms the soup base.' }),
};
