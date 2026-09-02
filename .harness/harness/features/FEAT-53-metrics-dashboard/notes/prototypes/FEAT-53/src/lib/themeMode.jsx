// The theme toggle's state. DESIGN.md §Component direction: "The theme toggle
// is an explicit control, defaulting to the OS preference on first load and
// persisting the user's choice in localStorage. Browser storage only."
//
// 'system' is Astryx's own OS-preference mode, so no component ever queries
// prefers-color-scheme and no component branches on isDark — the value that
// differs by theme differs in the token (DESIGN.md §C-3).

import {createContext, useCallback, useContext, useEffect, useMemo, useState} from 'react';

const KEY = 'feat-53-prototype-theme-mode';
export const THEME_MODES = ['system', 'light', 'dark'];

const ThemeModeContext = createContext({mode: 'system', setMode: () => {}});

export function ThemeModeProvider({children}) {
  const [mode, setModeState] = useState('system');

  // Read the persisted choice after mount so the first paint is the OS
  // preference rather than a flash of the wrong theme.
  useEffect(() => {
    const stored = globalThis.localStorage?.getItem(KEY);
    if (stored && THEME_MODES.includes(stored)) setModeState(stored);
  }, []);

  const setMode = useCallback((next) => {
    setModeState(next);
    globalThis.localStorage?.setItem(KEY, next);
  }, []);

  const value = useMemo(() => ({mode, setMode}), [mode, setMode]);
  return <ThemeModeContext.Provider value={value}>{children}</ThemeModeContext.Provider>;
}

export function useThemeMode() {
  return useContext(ThemeModeContext);
}
