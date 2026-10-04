import { useEffect, useState } from 'react';
import { guestStorageKey, newGuest, parseGuests, type Guest } from './mealmerge';

function loadGuests() {
  try { return { guests: parseGuests(localStorage.getItem(guestStorageKey)), warning: '' }; }
  catch { return { guests: [newGuest()], warning: 'Guest profiles could not be loaded. Guest choices start fresh; your Tasteprint is unchanged.' }; }
}

export function useMealMergeGuests() {
  const [initial] = useState(loadGuests);
  const [guests, setGuests] = useState<Guest[]>(initial.guests);
  const [warning, setWarning] = useState(initial.warning);
  useEffect(() => {
    try {
      // Blank name while typing is stored as its fallback, not an invalid record.
      localStorage.setItem(guestStorageKey, JSON.stringify({ version: 1, guests: guests.map(guest => ({
        ...guest, name: guest.name.trim() || `Guest ${guest.id.slice(-1)}`,
      })) }));
    } catch { setWarning('Browser storage is unavailable. Guest choices work for this visit but may not survive a refresh.'); }
  }, [guests]);
  return { guests, setGuests, warning };
}
