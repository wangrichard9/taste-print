import { describe, expect, it } from 'vitest';
import { catalog, reviewedCatalog } from '../data/catalog';
import { basicTastes, recipeSensoryNotes, sensoryVocabulary, sensoryVersion } from '../data/sensory';
import { describeSensory, sensoryNotesFor } from './sensory';

describe('controlled sensory evidence', () => {
  it('uses the agreed finite dictionary and exactly five basic tastes', () => {
    expect(sensoryVocabulary).toHaveLength(18);
    expect(new Set(sensoryVocabulary.map(term => term.id)).size).toBe(18);
    expect(basicTastes.map(term => term.id)).toEqual(['sweet', 'sour', 'salty', 'bitter', 'umami']);
    const ids = new Set<string>(sensoryVocabulary.map(term => term.id));
    expect(Object.keys(recipeSensoryNotes).sort()).toEqual(reviewedCatalog.map(dish => dish.id).sort());
    for (const annotation of Object.values(recipeSensoryNotes)) {
      expect(annotation.version).toBe(sensoryVersion);
      expect(annotation.basis).toBe('metadata-estimate');
      for (const [id, reason] of Object.entries(annotation.notes)) {
        expect(ids.has(id)).toBe(true);
        expect(reason?.length).toBeGreaterThan(10);
      }
    }
  });
  it('counts only explicit likes and retains the dishes behind each count', () => {
    const summary = describeSensory({ 'foodcom:90975': 'like', 'foodcom:28199': 'like', 'foodcom:60350': 'pass', missing: 'like' });
    expect(summary.liked).toHaveLength(2);
    expect(summary.annotatedCount).toBe(2);
    expect(summary.notes.find(note => note.id === 'herby')?.evidence.map(entry => entry.dish.id)).toEqual(['foodcom:90975', 'foodcom:28199']);
    expect(summary.notes.find(note => note.id === 'creamy')?.status).toBe('unassessed');
    for (const note of summary.notes) expect(note.count).toBe(note.evidence.length);
  });
  it('does not turn missing annotation, a bulk category, or no likes into a negative preference', () => {
    const bulk = catalog.find(dish => !dish.manuallyReviewed)!;
    const summary = describeSensory({ [bulk.id]: 'like' });
    expect(summary.liked).toHaveLength(1);
    expect(summary.annotatedCount).toBe(0);
    expect(summary.unannotatedCount).toBe(1);
    expect(summary.notes.every(note => note.status === 'unassessed' && note.count === 0)).toBe(true);
    expect(sensoryNotesFor(bulk)).toEqual([]);
    expect(describeSensory({}).notes.every(note => note.status === 'unassessed')).toBe(true);
  });
  it('does not infer salty from common seasoning or equate broad Savory with umami', () => {
    const salmon = reviewedCatalog.find(dish => dish.id === 'foodcom:28199')!;
    expect(salmon.ingredients).toContain('salt');
    expect(salmon.tags).toContain('Savory');
    expect(sensoryNotesFor(salmon)).not.toContain('Salty');
    expect(sensoryNotesFor(salmon)).not.toContain('Umami');
    expect(describeSensory({ [salmon.id]: 'like' }).notes.find(note => note.id === 'bitter')?.status).toBe('unassessed');
  });
});
