// The entry point index.html loads.
//
// One <Theme> for the whole app, one defineTheme call behind it, and `mode`
// from the explicit toggle — 'system' on first load, which is how the OS
// preference becomes the default without any component asking
// prefers-color-scheme (DESIGN.md §C-3).

import {StrictMode} from 'react';
import {createRoot} from 'react-dom/client';
import {RouterProvider} from '@tanstack/react-router';
import {Theme} from '@astryxdesign/core';
import '@astryxdesign/core/reset.css';
import '@astryxdesign/core/astryx.css';
import {metricsTheme} from './theme.js';
import {makeRouter} from './router.jsx';
import {ThemeModeProvider, useThemeMode} from './lib/themeMode.jsx';

const router = makeRouter();

function App() {
  const {mode} = useThemeMode();
  return (
    <Theme theme={metricsTheme} mode={mode}>
      <RouterProvider router={router} />
    </Theme>
  );
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ThemeModeProvider>
      <App />
    </ThemeModeProvider>
  </StrictMode>,
);
