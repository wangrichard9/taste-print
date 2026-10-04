import { describe, expect, it } from 'vitest';
import { catalog, reviewedCatalog } from '../data/catalog';
import { emptyTaste, storageKey } from './taste';
import { guestOpinion, guestStorageKey, groupRequest, memberReason, newGuest, parseGuests, parseGroupResult } from './mealmerge';

import { groupFixture } from '../test/groupFixture';

describe('local guests and group response contract', () => {
  it('keeps guest storage distinct and starts with an empty guest, never sample opinions', () => {
    expect(guestStorageKey).not.toBe(storageKey);
    expect(parseGuests(null)).toEqual([newGuest()]);
    expect(parseGuests(JSON.stringify({ version: 1, guests: [] }))).toEqual([]);
  });
  it('round-trips guests, trims names and discards unknown recipe opinions without reassignment', () => {
    const guest = { ...newGuest(), name: '  Maya  ', opinions: { [reviewedCatalog[0].id]: 'like', unknown: 'pass' } };
    expect(parseGuests(JSON.stringify({ version: 1, guests: [guest] }))).toEqual([{ ...guest, name: 'Maya', opinions: { [reviewedCatalog[0].id]: 'like' } }]);
  });
  it('rejects bad versions, identities, duplicates, names and oversized tables', () => {
    const bad = [{ version: 2, guests: [] }, { version: 1, guests: [newGuest(), newGuest()] },
      { version: 1, guests: [{ ...newGuest(), id: 'you' }] }, { version: 1, guests: [{ ...newGuest(), name: '' }] },
      { version: 1, guests: [newGuest(), newGuest('guest-2'), newGuest('guest-3'), newGuest('guest-4')] }];
    for (const record of bad) expect(() => parseGuests(JSON.stringify(record))).toThrow();
  });
  it('toggles/switches only the named guest without mutating personal or other guest choices', () => {
    const taste = emptyTaste(), guests = [newGuest(), newGuest('guest-2')], id = reviewedCatalog[0].id;
    const liked = guestOpinion(guests, 'guest-1', id, 'like');
    expect(liked[0].opinions[id]).toBe('like'); expect(liked[1]).toBe(guests[1]);
    expect(guests[0].opinions).toEqual({}); expect(taste.opinions).toEqual({});
    const passed = guestOpinion(liked, 'guest-1', id, 'pass'); expect(passed[0].opinions[id]).toBe('pass');
    expect(guestOpinion(passed, 'guest-1', id, 'pass')[0].opinions).toEqual({});
  });
  it('builds requests from explicit choices only; saves and blank-name drafts do not become taste', () => {
    const taste = { ...emptyTaste(), saved: [reviewedCatalog[0].id], opinions: { [reviewedCatalog[1].id]: 'like' as const } };
    const request = groupRequest(taste, [{ ...newGuest(), name: '' }], 'balanced');
    expect(request.members[0].likes).toEqual([reviewedCatalog[1].id]); expect(request.members[1].name).toBe('Guest 1');
    expect(request.members[1].likes).toEqual([]);
  });
  it('accepts full fallback and partial evidence without treating unknown members as dislikes', () => {
    const request = groupRequest(emptyTaste(), [newGuest()], 'balanced');
    const raw = groupFixture(request); expect(parseGroupResult(raw, request).fallbackCount).toBe(catalog.length);
    request.members[0].likes = [reviewedCatalog[0].id];
    const partial = parseGroupResult(groupFixture(request), request);
    expect(partial.items[0].basis).toBe('partial'); expect(partial.items[0].members[1].basis).toBe('unknown');
    expect(memberReason(partial.items[0].members[1], 0)).toContain('Not a dislike');
  });
  it('excludes a pass even if another member likes the recipe, and validates a genuinely empty pool', () => {
    const request = groupRequest(emptyTaste(), [newGuest()], 'overall');
    request.members[0].likes = [reviewedCatalog[0].id]; request.members[1].passes = [reviewedCatalog[0].id];
    expect(parseGroupResult(groupFixture(request), request).items.some(item => item.id === reviewedCatalog[0].id)).toBe(false);
    request.members[1].passes = catalog.map(dish => dish.id);
    expect(parseGroupResult(groupFixture(request), request).items).toEqual([]);
  });
  it('rejects incomplete/duplicate output, wrong priority, invented people and wrong evidence totals', () => {
    const request = groupRequest(emptyTaste(), [newGuest()], 'balanced');
    const incomplete = groupFixture(request); incomplete.items.pop();
    const duplicate = groupFixture(request); duplicate.items[1] = duplicate.items[0];
    const person = groupFixture(request); person.items[0].members[0].memberId = 'imaginary';
    const coverage = groupFixture(request); coverage.items[0].supportCount = 1;
    for (const raw of [incomplete, duplicate, person, coverage, { ...groupFixture(request), priority: 'overall' },
      { ...groupFixture(request), evidenceMemberCount: 1 }]) expect(() => parseGroupResult(raw, request)).toThrow();
  });
  it('validates positive shared-like evidence, positions and seed identity', () => {
    const request = groupRequest(emptyTaste(), [newGuest()], 'balanced'); request.members[0].likes = [reviewedCatalog[0].id];
    const raw = groupFixture(request); const dish = reviewedCatalog[1];
    const item = raw.items.find(item => item.id === dish.id)!;
    item.members[0] = { memberId: 'you', basis: 'co_like', position: 1, evidence: { seedId: reviewedCatalog[0].id, sharedLikers: 4 } };
    item.supportCount = 1; item.basis = 'partial'; raw.members[0].coLikeCount = 1; raw.fallbackCount--;
    raw.items.sort((a, b) => b.supportCount - a.supportCount);
    expect(parseGroupResult(raw, request).members[0].coLikeCount).toBe(1);
    item.members[0].evidence!.sharedLikers = 0; expect(() => parseGroupResult(raw, request)).toThrow();
    item.members[0].evidence!.sharedLikers = 4; item.members[0].position = 2; expect(() => parseGroupResult(raw, request)).toThrow();
  });
});
