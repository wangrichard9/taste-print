import { useEffect, useState } from 'react';
import { emptyTaste, parseTaste, storageKey } from './taste';

function loadLocalTaste() {
  try { return { state: parseTaste(localStorage.getItem(storageKey)), warning: '' }; }
  catch { return { state: emptyTaste(), warning: 'Your local profile could not be loaded. This session starts fresh.' }; }
}

export function useTaste() {
  const [initial] = useState(loadLocalTaste);
  const [taste, setTaste] = useState(initial.state);
  const [storageWarning, setStorageWarning] = useState(initial.warning);
  useEffect(() => {
    try { localStorage.setItem(storageKey, JSON.stringify(taste)); }
    catch { setStorageWarning('Browser storage is unavailable. Your choices work for this session but may not survive a refresh.'); }
  }, [taste]);
  return { taste, setTaste, storageWarning };
}
