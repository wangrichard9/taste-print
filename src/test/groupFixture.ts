import { catalog } from '../data/catalog';
import type { GroupRequest, GroupResult } from '../lib/mealmerge';

export function groupFixture(request: GroupRequest): GroupResult {
  const passed = new Set(request.members.flatMap(member => member.passes));
  const items = catalog.filter(dish => dish.modelSupported && !passed.has(dish.id)).map(dish => {
    const members = request.members.map(member => ({ memberId: member.id,
      basis: member.likes.includes(dish.id) ? 'known_like' as const : 'unknown' as const }));
    const supportCount = members.filter(member => member.basis !== 'unknown').length;
    return { id: dish.id, supportCount, basis: supportCount === request.members.length ? 'group' as const : supportCount ? 'partial' as const : 'popularity' as const, members };
  }).sort((a, b) => b.supportCount - a.supportCount);
  return { method: 'group_rules+raw_co_like', priority: request.priority, catalogSize: catalog.length,
    excludedCount: passed.size, evidenceMemberCount: request.members.filter(member => items.some(item => member.likes.includes(item.id))).length,
    maxSupportCount: Math.max(0, ...items.map(item => item.supportCount)), fallbackCount: items.filter(item => !item.supportCount).length,
    members: request.members.map(member => ({ id: member.id, name: member.name, supportedLikeCount: new Set(member.likes).size,
      unsupportedLikeCount: 0, coLikeCount: 0 })), items };
}
