import { dishById, type Dish } from '../data/catalog';
import { recipeSensoryNotes, sensoryVocabulary, type SensoryId } from '../data/sensory';
import type { Opinion } from './taste';

export function describeSensory(opinions: Record<string, Opinion>) {
  const liked = Object.entries(opinions).flatMap(([id, opinion]) => {
    const dish = dishById.get(id);
    return opinion === 'like' && dish ? [dish] : [];
  });
  const annotated = liked.filter(dish => recipeSensoryNotes[dish.id]);
  const notes = sensoryVocabulary.map(term => {
    const evidence = annotated.flatMap(dish => {
      const reason = recipeSensoryNotes[dish.id].notes[term.id];
      return reason ? [{ dish, reason }] : [];
    });
    return { ...term, count: evidence.length, evidence, status: evidence.length ? 'estimated' as const : 'unassessed' as const };
  });
  return { liked, annotatedCount: annotated.length, unannotatedCount: liked.length - annotated.length, notes };
}

export type SensorySummary = ReturnType<typeof describeSensory>;
export type SensoryNote = SensorySummary['notes'][number];
export function sensoryNotesFor(dish: Dish): string[] {
  const annotation = recipeSensoryNotes[dish.id];
  return annotation ? sensoryVocabulary.filter(term => annotation.notes[term.id]).map(term => term.label) : [];
}
export function sensoryHeading(summary: SensorySummary) {
  const words = summary.notes.filter(note => note.count && note.group !== 'taste')
    .sort((a, b) => b.count - a.count || a.label.localeCompare(b.label)).slice(0, 2);
  return words.length ? `${words.map(word => word.label).join(' & ')}.` : 'A taste of what makes you, you.';
}
export function findSensoryNote(summary: SensorySummary, id: SensoryId) {
  return summary.notes.find(note => note.id === id)!;
}
