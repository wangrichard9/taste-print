"""Pure content ranking shared by experiments and future Tasteprint serving.

Scores are cosine similarities, not probabilities. Saves/passes are not seed likes.
"""
import html
import math
import re

import numpy as np


def clean_text(value):
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def recipe_text(recipe):
    """Use source food metadata, never ratings, authors or editorial summaries."""
    return (f"Recipe: {clean_text(recipe['name'])}. "
            f"Ingredients: {', '.join(clean_text(x) for x in recipe['ingredients'])}. "
            f"Category: {clean_text(recipe.get('category'))}. "
            f"Tags: {', '.join(clean_text(x) for x in recipe.get('keywords', []))}.")


def content_signature(recipe):
    """Conservative exact-content deduplication; not a near-duplicate detector."""
    normalize = lambda text: re.sub(r"[^\w]+", " ", clean_text(text).casefold()).strip()
    return (normalize(recipe['name']), tuple(sorted(normalize(x) for x in recipe['ingredients'])))


def liked_profile(embeddings, seed_indices):
    seeds = list(dict.fromkeys(seed_indices))
    if not seeds:
        raise ValueError("At least one explicit liked recipe is required")
    if any(not isinstance(i, (int, np.integer)) or i < 0 or i >= len(embeddings) for i in seeds):
        raise ValueError("Seed recipe is outside the embedding catalog")
    profile = embeddings[seeds].mean(axis=0)
    norm = float(np.linalg.norm(profile))
    if not np.isfinite(norm) or norm <= 1e-8:
        raise ValueError("Liked recipes cannot form a finite nonzero profile")
    return profile / norm


def rank(scores, recipe_ids, seen_ids=(), k=10):
    """Rank by score descending, breaking ties by ascending source ID."""
    scores = np.asarray(scores)
    ids = np.asarray(recipe_ids)
    if scores.ndim != 1 or ids.ndim != 1 or len(scores) != len(ids) or len(set(ids.tolist())) != len(ids):
        raise ValueError("Scores and unique recipe IDs must be aligned one-dimensional arrays")
    if not isinstance(k, (int, np.integer)) or isinstance(k, bool) or k <= 0 or not np.isfinite(scores).all():
        raise ValueError("Ranking requires positive K and finite scores")
    eligible = np.flatnonzero(~np.isin(ids, list(seen_ids)))
    order = np.lexsort((ids[eligible], -scores[eligible]))[:k]
    return eligible[order]


def recommend(embeddings, recipe_ids, likes, seen_ids=(), k=10):
    index = {int(recipe_id): i for i, recipe_id in enumerate(recipe_ids)}
    likes = list(dict.fromkeys(likes))
    if any(recipe_id not in index for recipe_id in likes):
        raise ValueError("A liked recipe is not in this experiment's catalog")
    profile = liked_profile(embeddings, [index[recipe_id] for recipe_id in likes])
    scores = embeddings @ profile
    ranked = rank(scores, recipe_ids, set(seen_ids) | set(likes), k)
    return [(int(recipe_ids[i]), float(scores[i])) for i in ranked]


def ranking_metrics(recommendations, relevant, k=10):
    """Binary relevance; recall covers recorded held-out likes, not all taste."""
    relevant = set(relevant)
    recommendations = list(recommendations)[:k]
    if not relevant or k <= 0 or len(set(recommendations)) != len(recommendations):
        raise ValueError("Metrics require relevant items, positive K and unique recommendations")
    hits = [recipe_id in relevant for recipe_id in recommendations]
    dcg = sum(hit / math.log2(position + 2) for position, hit in enumerate(hits))
    ideal = sum(1 / math.log2(position + 2) for position in range(min(k, len(relevant))))
    return {"precision": sum(hits) / k, "recall": sum(hits) / len(relevant),
            "ndcg": dcg / ideal, "hit_rate": float(any(hits))}
