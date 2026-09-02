import {useEffect, useRef, useState} from 'react';

/**
 * CAP-13: charts fill their container width and no chart has a fixed pixel
 * width, so the SVG needs the measured width rather than a constant. The
 * fallback is only used before the first measurement.
 */
export function useContainerWidth(fallback = 960) {
  const ref = useRef(null);
  const [width, setWidth] = useState(fallback);

  useEffect(() => {
    const node = ref.current;
    if (!node || typeof ResizeObserver === 'undefined') return undefined;
    const observer = new ResizeObserver((entries) => {
      const next = entries[0]?.contentRect.width;
      if (next && next > 0) setWidth(next);
    });
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return [ref, width];
}
