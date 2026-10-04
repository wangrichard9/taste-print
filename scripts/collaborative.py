"""Small rating-trained module: fit recipe factors, fold in likes, blend scores.

Binary CSR positives; weighted implicit ALS. Missing feedback is weak evidence,
not an explicit dislike. Outputs are ranking scores, never probabilities.
"""
from dataclasses import dataclass

import numpy as np
from scipy.sparse import csr_matrix
from scipy.stats import rankdata
from threadpoolctl import threadpool_limits


@dataclass
class FactorModel:
    users: np.ndarray
    items: np.ndarray
    objectives: list[float]
    alpha: float
    regularization: float


def _positives(matrix):
    matrix = csr_matrix(matrix, dtype=np.float64, copy=True)
    matrix.sum_duplicates()
    matrix.eliminate_zeros()
    matrix.sort_indices()
    if min(matrix.shape) < 1 or not matrix.nnz or not np.isfinite(matrix.data).all() or (matrix.data <= 0).any():
        raise ValueError('A nonempty finite positive interaction matrix is required')
    matrix.data[:] = 1.0
    return matrix


def _update(positives, fixed, alpha, regularization, block_size=512):
    dimensions = fixed.shape[1]
    base = fixed.T @ fixed + regularization * np.eye(dimensions)
    result = np.empty((positives.shape[0], dimensions), dtype=np.float64)
    for start in range(0, len(result), block_size):
        stop = min(start + block_size, len(result))
        systems = np.broadcast_to(base, (stop - start, dimensions, dimensions)).copy()
        targets = np.zeros((stop - start, dimensions), dtype=np.float64)
        for local, row in enumerate(range(start, stop)):
            liked = fixed[positives.indices[positives.indptr[row]:positives.indptr[row + 1]]]
            systems[local] += alpha * (liked.T @ liked)
            targets[local] = (1 + alpha) * liked.sum(axis=0)
        result[start:stop] = np.linalg.solve(systems, targets[..., None])[..., 0]
    return result


def objective(positives, users, items, alpha, regularization):
    """Exact objective without materializing the dense users-by-items matrix."""
    base = np.sum((users.T @ users) * (items.T @ items))
    correction = 0.0
    for row in range(positives.shape[0]):
        liked = positives.indices[positives.indptr[row]:positives.indptr[row + 1]]
        scores = items[liked] @ users[row]
        correction += np.sum(alpha * scores**2 - 2 * (1 + alpha) * scores + (1 + alpha))
    return float(base + correction + regularization * (np.sum(users**2) + np.sum(items**2)))


def fit(positives, *, dimensions=32, iterations=12, alpha=20.0, regularization=1.0,
        seed=20260930, progress=None):
    positives = _positives(positives)
    if (not isinstance(dimensions, int) or dimensions < 1 or not isinstance(iterations, int)
            or iterations < 1 or not np.isfinite([alpha, regularization]).all()
            or alpha < 0 or regularization <= 0):
        raise ValueError('Positive dimensions/iterations/regularization and nonnegative confidence required')
    transposed = positives.T.tocsr()
    items = np.random.default_rng(seed).normal(0, .01, (positives.shape[1], dimensions))
    users = np.zeros((positives.shape[0], dimensions))
    objectives = []
    with threadpool_limits(limits=1):
        objectives.append(objective(positives, users, items, alpha, regularization))
        for step in range(iterations):
            users = _update(positives, items, alpha, regularization)
            items = _update(transposed, users, alpha, regularization)
            loss = objective(positives, users, items, alpha, regularization)
            if not np.isfinite(loss) or loss > objectives[-1] + 1e-8 * max(1, abs(objectives[-1])):
                raise ValueError('ALS objective is non-finite or increased')
            objectives.append(loss)
            if progress:
                progress(step + 1, loss)
    return FactorModel(users, items, objectives, alpha, regularization)


def fold_in(items, seed_profiles, *, alpha=20.0, regularization=1.0):
    """Infer factors from known recipe-index likes only; empty/unknown seeds fail."""
    items = np.asarray(items, dtype=np.float64)
    if (items.ndim != 2 or min(items.shape) < 1 or not np.isfinite(items).all()
            or not np.isfinite([alpha, regularization]).all() or alpha < 0 or regularization <= 0):
        raise ValueError('Finite item factors and valid confidence/regularization required')
    row_indices, col_indices = [], []
    profiles = list(seed_profiles)
    if not profiles:
        raise ValueError('At least one profile is required')
    for row, seeds in enumerate(profiles):
        seeds = list(seeds)
        if not seeds or any(not isinstance(i, (int, np.integer)) or i < 0 or i >= len(items) for i in seeds):
            raise ValueError('Each profile needs known integer recipe-index likes')
        unique = sorted(set(seeds))
        row_indices.extend([row] * len(unique))
        col_indices.extend(unique)
    positive = csr_matrix((np.ones(len(col_indices)), (row_indices, col_indices)), shape=(len(profiles), len(items)))
    with threadpool_limits(limits=1):
        return _update(positive, items, alpha, regularization)


def blend_scores(content, collaborative, cf_weight, eligible=None):
    """Within-profile percentile rank blend; eligibility is only seen exclusion."""
    content = np.asarray(content, dtype=float)
    collaborative = np.asarray(collaborative, dtype=float)
    if (content.ndim != 1 or content.shape != collaborative.shape or not content.size
            or not np.isfinite(content).all() or not np.isfinite(collaborative).all()
            or not np.isfinite(cf_weight) or not 0 <= cf_weight <= 1):
        raise ValueError('Aligned finite scores and a blend weight in [0,1] required')
    eligible = np.ones(content.size, dtype=bool) if eligible is None else np.asarray(eligible, dtype=bool)
    if eligible.shape != content.shape or not eligible.any():
        raise ValueError('An aligned nonempty candidate eligibility mask is required')
    if cf_weight in (0, 1):
        return (content if cf_weight == 0 else collaborative).copy()
    count = int(eligible.sum())
    result = np.zeros_like(content)
    result[eligible] = ((1 - cf_weight) * rankdata(content[eligible], method='average')
                        + cf_weight * rankdata(collaborative[eligible], method='average')) / count
    return result
