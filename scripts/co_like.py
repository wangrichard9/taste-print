"""Direct fitting-only recipe relationships behind a small scoring interface."""
import numpy as np
from scipy.sparse import csr_matrix

MODES = ('raw', 'cosine_shrunk')


def fit_relationships(positives, mode='cosine_shrunk', shrinkage=10.0):
    positive = csr_matrix(positives, dtype=np.float64, copy=True)
    positive.sum_duplicates()
    positive.eliminate_zeros()
    positive.sort_indices()
    if (min(positive.shape) < 1 or not positive.nnz or not np.isfinite(positive.data).all()
            or (positive.data <= 0).any() or mode not in MODES
            or not np.isfinite(shrinkage) or shrinkage < 0):
        raise ValueError('Finite positive interactions, a known mode and nonnegative shrinkage required')
    positive.data[:] = 1
    counts = np.asarray(positive.sum(axis=0)).ravel()
    relationships = (positive.T @ positive).tocsr()
    relationships.setdiag(0)
    relationships.eliminate_zeros()
    relationships.sort_indices()
    if mode == 'cosine_shrunk':
        rows = np.repeat(np.arange(len(counts)), np.diff(relationships.indptr))
        support = relationships.data.copy()
        relationships.data /= np.sqrt(counts[rows] * counts[relationships.indices])
        relationships.data *= support / (support + shrinkage)
    return relationships


def score_likes(relationships, seed_profiles):
    """Mean known seed relationships; scores are not probabilities."""
    relationships = csr_matrix(relationships, dtype=np.float64)
    if (relationships.shape[0] != relationships.shape[1] or not relationships.shape[0]
            or not np.isfinite(relationships.data).all() or (relationships.data < 0).any()):
        raise ValueError('A finite nonnegative square relationship matrix is required')
    profiles = list(seed_profiles)
    if not profiles:
        raise ValueError('At least one profile is required')
    scores = []
    for seeds in profiles:
        seeds = list(seeds)
        if not seeds or any(not isinstance(i, (int, np.integer)) or i < 0 or i >= relationships.shape[0] for i in seeds):
            raise ValueError('Profiles require known integer seed indices')
        scores.append(np.asarray(relationships[sorted(set(seeds))].mean(axis=0)).ravel())
    return np.stack(scores)
