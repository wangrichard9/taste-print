import { useEffect, useState } from 'react';
import type { Dish } from '../data/catalog';

export default function SourceDirections({ dish }: { dish: Dish }) {
  const [steps, setSteps] = useState<string[] | null>(null);
  const [failed, setFailed] = useState(false);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    setSteps(null); setFailed(false);
    if (dish.manuallyReviewed) return;
    const controller = new AbortController();
    let timedOut = false;
    let cancelled = false;
    const timer = window.setTimeout(() => { timedOut = true; controller.abort(); }, 10000);
    fetch(`/api/recipes/${dish.sourceRecipeId}`, { signal: controller.signal }).then(async response => {
      if (!response.ok) throw new Error('Source unavailable');
      const result: unknown = await response.json();
      if (!result || typeof result !== 'object') throw new Error('Invalid source');
      const detail = result as Dish;
      if (detail.id !== dish.id || !Array.isArray(detail.instructions) || detail.instructions.some(step => typeof step !== 'string')) throw new Error('Invalid directions');
      if (!cancelled && !controller.signal.aborted) setSteps(detail.instructions);
    }).catch(() => { if (!cancelled && (!controller.signal.aborted || timedOut)) setFailed(true); }).finally(() => window.clearTimeout(timer));
    return () => { cancelled = true; window.clearTimeout(timer); controller.abort(); };
  }, [dish.id, dish.manuallyReviewed, dish.sourceRecipeId, attempt]);
  const directions = dish.manuallyReviewed ? dish.instructions : steps;
  return <><h2>Directions from the source</h2>
    {failed ? <p className="evidence-note" role="alert">Local directions are unavailable. Use the original recipe link below, or <button className="text-link" type="button" onClick={() => setAttempt(value => value + 1)}>retry</button>.</p>
      : directions === null ? <p className="evidence-note" role="status">Loading source directions…</p>
      : directions.length ? <ol className="recipe-directions">{directions.map((instruction, index) => <li key={index}>{instruction}</li>)}</ol>
      : <p className="evidence-note">Directions were not provided in this source record. Consult the original recipe.</p>}
  </>;
}
