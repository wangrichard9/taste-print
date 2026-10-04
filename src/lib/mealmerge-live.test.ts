import { expect, it } from 'vitest';
import { reviewedCatalog } from '../data/catalog';
import { emptyTaste } from './taste';
import { groupRequest, newGuest, parseGroupResult, type GroupRequest } from './mealmerge';

it.skipIf(import.meta.env.VITE_TASTEPRINT_LIVE_TEST !== '1')('decodes actual group policies and blank-guest evidence through Vite', async () => {
  const taste = emptyTaste();
  for (const dish of reviewedCatalog.slice(0, 6)) taste.opinions[dish.id] = 'like';
  const guest = newGuest();
  for (const index of [8, 16, 22, 26]) guest.opinions[reviewedCatalog[index].id] = 'like';
  guest.opinions[reviewedCatalog[1].id] = 'pass';
  const fetchGroup = async (input: GroupRequest) => {
    const response = await fetch('http://127.0.0.1:5173/api/mealmerge', { method: 'POST',
      headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(input), signal: AbortSignal.timeout(10000) });
    expect(response.ok).toBe(true); return parseGroupResult(await response.json(), input);
  };
  const balanced = await fetchGroup(groupRequest(taste, [guest], 'balanced'));
  const overall = await fetchGroup(groupRequest(taste, [guest], 'overall'));
  expect(balanced.maxSupportCount).toBe(2); expect(balanced.excludedCount).toBe(1);
  expect(balanced.items.some(item => item.id === reviewedCatalog[1].id)).toBe(false);
  expect(balanced.items.map(item => item.id)).not.toEqual(overall.items.map(item => item.id));
  const blank = await fetchGroup(groupRequest(taste, [guest, newGuest('guest-2')], 'balanced'));
  expect(blank.evidenceMemberCount).toBe(2);
  expect(blank.items.every(item => item.members[2].basis === 'unknown')).toBe(true);
  expect(blank.items.map(item => item.id)).toEqual(balanced.items.map(item => item.id));
}, 30000);
