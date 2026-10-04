"""Conservative named-ingredient retrieval. No semantic model or substitutions."""
from collections import defaultdict
import html
import re

PRIORITIES = ('balanced', 'ingredients', 'taste')
PLURALS = {'tomatoes': 'tomato', 'potatoes': 'potato', 'onions': 'onion', 'carrots': 'carrot',
           'eggs': 'egg', 'chickpeas': 'chickpea', 'beans': 'bean', 'peppers': 'pepper',
           'mushrooms': 'mushroom', 'lemons': 'lemon', 'limes': 'lime', 'apples': 'apple',
           'breasts': 'breast', 'thighs': 'thigh', 'cloves': 'clove', 'scallions': 'scallion',
           'lentils': 'lentil', 'cucumbers': 'cucumber', 'zucchinis': 'zucchini', 'chilis': 'chili'}
PREPARATION = {'chopped', 'diced', 'sliced', 'minced', 'fresh', 'large', 'small', 'medium'}
ALIASES = {'garbanzo bean': 'chickpea', 'scallion': 'green onion', 'spring onion': 'green onion',
           'garlic clove': 'garlic'}
# Explicit name-family matches only. A family match is not a guarantee that forms
# or cuts are interchangeable in cooking. Processed products are not expanded:
# tomato does not match tomato paste/sauce; milk does not match plant milks.
FAMILIES = {
    'tomato': ('cherry tomato', 'roma tomato', 'plum tomato', 'grape tomato'),
    'onion': ('red onion', 'yellow onion', 'white onion', 'sweet onion'),
    'chicken': ('chicken breast', 'boneless chicken breast', 'skinless chicken breast',
                'boneless skinless chicken breast', 'chicken thigh', 'boneless chicken thigh',
                'boneless skinless chicken thigh'),
    'milk': ('whole milk', 'skim milk', 'low fat milk', 'lowfat milk', '2 milk'),
    'egg': ('whole egg',),
}


def canonical_name(value):
    value = html.unescape(value).casefold()
    tokens = re.sub(r'[^\w]+', ' ', value, flags=re.UNICODE).split()
    tokens = [PLURALS.get(token, token) for token in tokens if token not in PREPARATION]
    phrase = ' '.join(tokens)
    return ALIASES.get(phrase, phrase)


def ingredient_inputs(values):
    if not isinstance(values, list) or not 1 <= len(values) <= 12:
        raise ValueError('Enter one to twelve ingredient names')
    unique = {}
    for value in values:
        if not isinstance(value, str):
            raise ValueError('Ingredient names must be text')
        label = ' '.join(value.split())
        name = canonical_name(label)
        if not label or len(label) > 40 or not name or not any(char.isalpha() for char in name):
            raise ValueError('Ingredient names must be nonempty text under 40 characters')
        unique.setdefault(name, label)
    return unique


class IngredientIndex:
    def __init__(self, dishes):
        self.sources = {}
        self.lookup = defaultdict(list)
        for dish in dishes:
            # Repeated source entries do not inflate matches or additional counts.
            rows = {}
            for value in dish['ingredients']:
                name = canonical_name(value)
                if name:
                    rows.setdefault(name, value)
            self.sources[dish['id']] = rows
            for name in rows:
                self.lookup[name].append(dish['id'])

    def match(self, values):
        queries = ingredient_inputs(values)
        found = {}
        for query, label in queries.items():
            forms = (query, *FAMILIES.get(query, ()))
            for form in forms:
                for recipe_id in self.lookup.get(form, ()):
                    entry = found.setdefault(recipe_id, {'matchedInputs': set(), 'matches': [], 'sourceKeys': set()})
                    entry['matchedInputs'].add(label)
                    entry['sourceKeys'].add(form)
                    entry['matches'].append({'input': label, 'recipeIngredient': self.sources[recipe_id][form]})
        result = {}
        for recipe_id, entry in found.items():
            result[recipe_id] = {
                'matchedInputs': [label for label in queries.values() if label in entry['matchedInputs']],
                'matches': entry['matches'],
                # Count a maximum one-to-one assignment: overlapping queries and
                # multiple varieties of one ingredient cannot inflate coverage.
                'matchCount': distinct_match_count(entry['matches']),
                'additionalIngredients': [value for name, value in self.sources[recipe_id].items() if name not in entry['sourceKeys']],
            }
        return list(queries.values()), result


def distinct_match_count(matches):
    options = defaultdict(set)
    for match in matches:
        options[match['input']].add(canonical_name(match['recipeIngredient']))
    assigned = {}

    def assign(label, visited):
        for source in sorted(options[label]):
            if source in visited:
                continue
            visited.add(source)
            if source not in assigned or assign(assigned[source], visited):
                assigned[source] = label
                return True
        return False

    return sum(assign(label, set()) for label in options)


def priority_key(item, priority):
    if priority not in PRIORITIES:
        raise ValueError('Unknown ingredient priority')
    ingredient_key = -item['matchCount']
    additional = len(item['additionalIngredients'])
    # Explicit likes are known evidence; direct co-likes are ranked predictions;
    # otherwise training popularity is only a fallback, never a taste probability.
    taste = (0 if item['knownLike'] else 1 if item['score'] > 0 else 2,
             -item['score'], -item['popularity'] if item['score'] <= 0 else 0)
    identity = item['sourceRecipeId']
    if priority == 'ingredients':
        return ingredient_key, additional, taste, identity
    if priority == 'taste':
        return taste, ingredient_key, additional, identity
    return ingredient_key, taste, additional, identity
