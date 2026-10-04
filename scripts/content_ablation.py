"""Pure registered ML 02 probes. No target labels enter profile scoring."""
import numpy as np

from recommendation import clean_text


def ingredient_text(recipe):
    return f"Ingredients: {', '.join(clean_text(x) for x in recipe['ingredients'])}."


def profile_scores(embeddings, seed_indices, mode):
    vectors = np.asarray(embeddings)
    seeds = np.asarray(seed_indices)
    if (vectors.ndim != 2 or not np.isfinite(vectors).all()
            or not np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-5)
            or seeds.ndim != 2 or seeds.shape[1] < 1
            or not np.issubdtype(seeds.dtype, np.integer)
            or np.any(seeds < 0) or np.any(seeds >= len(vectors))
            or any(len(set(row.tolist())) != len(row) for row in seeds)):
        raise ValueError('Scoring requires normalized vectors and valid unique liked indices')
    selected = vectors[seeds]
    if mode == 'centroid':
        profiles = selected.mean(axis=1)
        norms = np.linalg.norm(profiles, axis=1, keepdims=True)
        if np.any(norms <= 1e-8):
            raise ValueError('Likes cannot form a nonzero centroid')
        return (profiles / norms) @ vectors.T
    similarities = (selected.reshape(-1, vectors.shape[1]) @ vectors.T).reshape(len(seeds), seeds.shape[1], len(vectors))
    if mode == 'closest':
        return similarities.max(axis=1)
    if mode == 'top_two' and seeds.shape[1] >= 2:
        return np.partition(similarities, -2, axis=1)[:, -2:, :].mean(axis=1)
    raise ValueError('Unknown scoring mode or too few likes for top-two scoring')


def shuffled_profile_indices(count, seed):
    if count < 2:
        raise ValueError('A shuffled control requires at least two people')
    order = np.random.default_rng(seed).permutation(count)
    result = np.empty(count, dtype=int)
    result[order] = np.roll(order, 1)
    return result


def score_auc(high, lower):
    if not len(high) or not len(lower):
        return None
    difference = np.asarray(high)[:, None] - np.asarray(lower)[None, :]
    return float(np.mean((difference > 0).astype(float) + .5 * (difference == 0)))


def status_counts(recommendations, future_ratings):
    counts = {'known_high': 0, 'known_lower': 0, 'unknown': 0}
    for recipe_id in recommendations:
        rating = future_ratings.get(recipe_id)
        counts['unknown' if rating is None else 'known_high' if rating >= 4 else 'known_lower'] += 1
    return counts
