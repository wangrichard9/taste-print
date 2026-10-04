import { useState } from 'react';
import { ImageOff } from 'lucide-react';
import type { Dish } from '../data/catalog';

export default function DishImage({ dish, eager = false }: { dish: Dish; eager?: boolean }) {
  const [failed, setFailed] = useState(false);
  return failed || !dish.image ? <div className="image-fallback"><ImageOff aria-hidden="true" size={24} /><span>Photo unavailable</span></div>
    : <img src={dish.image} alt={dish.imageAlt} loading={eager ? 'eager' : 'lazy'} decoding="async"
      referrerPolicy="no-referrer" onError={() => setFailed(true)} />;
}
