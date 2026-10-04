import { catalog, dishById } from '../data/catalog';
import { recipeChoices, recommendationReason } from './discovery';
import { emptyTaste, setOpinion, type Opinion, type TasteState } from './taste';

export type Guest = { id: string; name: string; opinions: Record<string, Opinion> };
export type GroupPriority = 'balanced' | 'overall';
export type GroupMember = { id: string; name: string; likes: string[]; passes: string[] };
export type GroupRequest = { priority: GroupPriority; members: GroupMember[] };
export type MemberEvidence = { memberId: string; basis: 'known_like' | 'co_like' | 'unknown';
  position?: number; evidence?: { seedId: string; sharedLikers: number } };
export type GroupItem = { id: string; supportCount: number; basis: 'group' | 'partial' | 'popularity'; members: MemberEvidence[] };
export type GroupResult = { method: 'group_rules+raw_co_like'; priority: GroupPriority; catalogSize: number;
  excludedCount: number; evidenceMemberCount: number; maxSupportCount: number; fallbackCount: number;
  members: { id: string; name: string; supportedLikeCount: number; unsupportedLikeCount: number; coLikeCount: number }[];
  items: GroupItem[] };

export const guestStorageKey = 'tasteprint:mealmerge:foodcom:v2';
export const newGuest = (id = 'guest-1'): Guest => ({ id, name: `Guest ${id.slice(-1)}`, opinions: {} });

export function parseGuests(raw: string | null): Guest[] {
  if (!raw) return [newGuest()];
  const data = JSON.parse(raw);
  if (!data || data.version !== 1 || !Array.isArray(data.guests) || data.guests.length > 3) throw new Error('Invalid guest record');
  const ids = new Set<string>();
  return data.guests.map((guest: Guest) => {
    if (!guest || !['guest-1', 'guest-2', 'guest-3'].includes(guest.id) || ids.has(guest.id)
      || typeof guest.name !== 'string' || !guest.name.trim() || guest.name.length > 30
      || !guest.opinions || typeof guest.opinions !== 'object' || Array.isArray(guest.opinions)) throw new Error('Invalid guest');
    ids.add(guest.id);
    return { id: guest.id, name: guest.name.trim(), opinions: Object.fromEntries(Object.entries(guest.opinions)
      .filter(([id, opinion]) => dishById.has(id) && (opinion === 'like' || opinion === 'pass'))) };
  });
}

export function guestOpinion(guests: Guest[], guestId: string, dishId: string, opinion: Opinion): Guest[] {
  return guests.map(guest => guest.id !== guestId ? guest : { ...guest,
    opinions: setOpinion({ ...emptyTaste(), opinions: guest.opinions }, dishId, opinion).opinions });
}

export function groupRequest(taste: TasteState, guests: Guest[], priority: GroupPriority): GroupRequest {
  return { priority, members: [{ id: 'you', name: 'You', ...recipeChoices(taste) }, ...guests.map(guest => ({
    id: guest.id, name: guest.name.trim() || `Guest ${guest.id.slice(-1)}`,
    ...recipeChoices({ ...emptyTaste(), opinions: guest.opinions }),
  }))] };
}

export function parseGroupResult(raw: unknown, request: GroupRequest): GroupResult {
  if (!raw || typeof raw !== 'object') throw new Error('Invalid group response');
  const result = raw as GroupResult;
  const model = catalog.filter(dish => dish.modelSupported);
  const passed = new Set(request.members.flatMap(member => member.passes).filter(id => dishById.get(id)?.modelSupported));
  const integer = (value: number, max: number) => Number.isInteger(value) && value >= 0 && value <= max;
  if (result.method !== 'group_rules+raw_co_like' || result.priority !== request.priority
    || result.catalogSize !== model.length || result.excludedCount !== passed.size
    || !Array.isArray(result.members) || result.members.length !== request.members.length
    || !Array.isArray(result.items) || result.items.length !== model.length - passed.size
    || !integer(result.evidenceMemberCount, request.members.length)
    || !integer(result.maxSupportCount, request.members.length) || !integer(result.fallbackCount, result.items.length)) throw new Error('Invalid group metadata');
  const ids = new Set<string>();
  for (const [i, member] of result.members.entries()) {
    const input = request.members[i];
    const supported = new Set(input.likes.filter(id => dishById.get(id)?.modelSupported));
    if (!member || member.id !== input.id || member.name !== input.name || member.supportedLikeCount !== supported.size
      || member.unsupportedLikeCount !== new Set(input.likes).size - supported.size
      || !integer(member.coLikeCount, model.length - new Set([...input.likes, ...input.passes].filter(id => dishById.get(id)?.modelSupported)).size)) throw new Error('Invalid member summary');
  }
  let maxSupport = 0, fallback = 0, lastSupport = request.members.length;
  const contributors = new Set<string>();
  for (const item of result.items) {
    if (!item || !dishById.get(item.id)?.modelSupported || ids.has(item.id) || passed.has(item.id)
      || !integer(item.supportCount, request.members.length) || item.supportCount > lastSupport
      || !Array.isArray(item.members) || item.members.length !== request.members.length) throw new Error('Invalid shared recipe');
    ids.add(item.id); lastSupport = item.supportCount;
    let support = 0;
    for (const [i, row] of item.members.entries()) {
      const input = request.members[i];
      if (!row || row.memberId !== input.id || !['known_like', 'co_like', 'unknown'].includes(row.basis)
        || (row.basis === 'known_like') !== input.likes.includes(item.id)) throw new Error('Invalid member evidence');
      if (row.basis === 'co_like') {
        if (!integer(row.position!, result.members[i].coLikeCount) || row.position! < 1 || !row.evidence
          || !input.likes.includes(row.evidence.seedId) || !dishById.get(row.evidence.seedId)?.modelSupported
          || !Number.isInteger(row.evidence.sharedLikers) || row.evidence.sharedLikers <= 0) throw new Error('Invalid shared-like evidence');
      } else if (row.position !== undefined || row.evidence !== undefined) throw new Error('Unknown/explicit likes do not have predicted positions');
      if (row.basis !== 'unknown') { support++; contributors.add(input.id); }
    }
    const basis = support === request.members.length ? 'group' : support ? 'partial' : 'popularity';
    if (support !== item.supportCount || item.basis !== basis) throw new Error('Invalid coverage label');
    maxSupport = Math.max(maxSupport, support); if (!support) fallback++;
  }
  if (maxSupport !== result.maxSupportCount || fallback !== result.fallbackCount
    || contributors.size !== result.evidenceMemberCount) throw new Error('Invalid evidence totals');
  return result;
}

export function memberReason(row: MemberEvidence, count: number) {
  if (row.basis === 'known_like') return 'Already liked this recipe.';
  if (row.basis === 'unknown') return 'Unknown · no personal shared-like evidence. Not a dislike.';
  return `Position ${row.position!.toLocaleString()} of ${count.toLocaleString()} shared-like matches (ties share a position). ${recommendationReason({ id: '', basis: 'co_like', evidence: row.evidence })}`;
}
