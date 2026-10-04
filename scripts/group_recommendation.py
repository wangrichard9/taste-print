"""Explicit group policies over frozen individual co-likes; no fitting/evaluation."""
import math
import numpy as np

GROUP_PRIORITIES = ('balanced', 'overall')


def relative_positions(scores, eligible):
    """Tie-aware rank within positive unseen/unpassed matches, not probabilities."""
    values = np.asarray(scores)[eligible]
    count = len(values)
    positions = np.zeros(len(scores), dtype=np.int64)
    fits = np.full(len(scores), np.nan)
    if count:
        positions[eligible] = count - np.searchsorted(np.sort(values), values, side='right') + 1
        fits[eligible] = 1 - (positions[eligible] - 1) / count
    return positions, fits, count


def aggregate_key(coverage, weakest, average, popularity, recipe_id, priority):
    if priority not in GROUP_PRIORITIES:
        raise ValueError('Unknown group priority')
    # Treat mathematically tied rank fractions as ties despite float arithmetic.
    weakest, average = round(weakest, 12), round(average, 12)
    positions = (-weakest, -average) if priority == 'balanced' else (-average, -weakest)
    return -coverage, *positions, -popularity, recipe_id


def group_recommendations(engine, payload):
    if not isinstance(payload, dict) or set(payload) - {'members', 'priority'}:
        raise ValueError('Unexpected group fields')
    priority = payload.get('priority', 'balanced')
    members = payload.get('members')
    if priority not in GROUP_PRIORITIES or not isinstance(members, list) or not 2 <= len(members) <= 4:
        raise ValueError('Choose a priority and two to four members')
    member_ids = set()
    prepared = []
    # Validate the whole request before scoring any member.
    for member in members:
        if not isinstance(member, dict) or set(member) != {'id', 'name', 'likes', 'passes'}:
            raise ValueError('Invalid group member')
        member_id, name = member['id'], member['name']
        if (not isinstance(member_id, str) or not 1 <= len(member_id) <= 40 or member_id in member_ids
                or not isinstance(name, str) or not name.strip() or len(name) > 30):
            raise ValueError('Invalid member identity')
        for kind in ('likes', 'passes'):
            values = member[kind]
            if (not isinstance(values, list) or len(values) > len(engine.dishes)
                    or any(not isinstance(value, str) or value not in engine.dishes for value in values)):
                raise ValueError('Invalid member choices')
        if set(member['likes']) & set(member['passes']):
            raise ValueError('Conflicting member choices')
        member_ids.add(member_id)
        prepared.append({**member, 'name': name.strip()})

    rejected = {value for member in prepared for value in member['passes'] if value in engine.index}
    candidate_indices = [i for i, value in enumerate(engine.ids) if f'foodcom:{value}' not in rejected]
    evidence_rows, fit_rows, summaries = [], [], []
    for member in prepared:
        choices, likes, scores, seed_weights = engine.choice_context(
            {'likes': member['likes'], 'passes': member['passes']}, dense_evidence=False)
        eligible = scores > 0
        for value in choices['likes'] | choices['passes']:
            if value in engine.index:
                eligible[engine.index[value]] = False
        positions, fits, count = relative_positions(scores, eligible)
        rows = []
        for i, recipe_id in enumerate(engine.ids):
            recipe_key = f'foodcom:{recipe_id}'
            row = {'memberId': member['id'], 'basis': 'unknown'}
            if recipe_key in choices['likes']:
                fits[i] = 1
                row['basis'] = 'known_like'
            elif eligible[i]:
                column = seed_weights.getcol(i)
                strongest = int(column.indices[np.argmax(column.data)])
                row.update(basis='co_like', position=int(positions[i]),
                           evidence={'seedId': likes[strongest], 'sharedLikers': int(column.data.max())})
            rows.append(row)
        evidence_rows.append(rows)
        fit_rows.append(fits)
        summaries.append({'id': member['id'], 'name': member['name'], 'supportedLikeCount': len(likes),
                          'unsupportedLikeCount': len(choices['likes']) - len(likes), 'coLikeCount': count})

    fits = np.array(fit_rows)
    counts = np.isfinite(fits).sum(axis=0)
    # Compensated sums keep the aggregate invariant to member display order.
    averages = np.array([math.fsum(float(value) for value in fits[:, i] if np.isfinite(value)) / int(counts[i])
                         if counts[i] else 0 for i in range(len(engine.ids))])
    weakest = np.min(np.where(np.isfinite(fits), fits, np.inf), axis=0)
    weakest[counts == 0] = 0  # Sorting sentinel only; missing member values stay NaN.
    order = sorted(candidate_indices, key=lambda i: aggregate_key(int(counts[i]), float(weakest[i]),
        float(averages[i]), float(engine.popularity[i]), int(engine.ids[i]), priority))
    items = [{'id': f'foodcom:{engine.ids[i]}', 'supportCount': int(counts[i]),
              'basis': 'group' if counts[i] == len(prepared) else 'partial' if counts[i] else 'popularity',
              'members': [rows[i] for rows in evidence_rows]} for i in order]
    return {'method': 'group_rules+raw_co_like', 'priority': priority, 'catalogSize': len(engine.ids),
            'excludedCount': len(rejected), 'members': summaries,
            'evidenceMemberCount': sum(any(rows[i]['basis'] != 'unknown' for i in candidate_indices) for rows in evidence_rows),
            'maxSupportCount': max((item['supportCount'] for item in items), default=0),
            'fallbackCount': sum(item['basis'] == 'popularity' for item in items), 'items': items}
