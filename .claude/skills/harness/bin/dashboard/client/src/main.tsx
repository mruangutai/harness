import '@astryxdesign/core/reset.css';
import '@astryxdesign/core/astryx.css';
import '@astryxdesign/theme-neutral/theme.css';
import './dashboard.css';

import { Theme } from '@astryxdesign/core';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider } from '@tanstack/react-router';
import { useLayoutEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { makeRouter } from './routes';
import { metricsTheme, metricsTokens } from './theme';
document.documentElement.setAttribute('data-astryx-theme', 'metrics-dashboard');

const root = document.getElementById('root');
if (!root) throw new Error('Missing dashboard root');

const queryClient = new QueryClient({ defaultOptions: { queries: { refetchInterval: false } } });
const themeTokens = ['--color-background-card', '--color-neutral', '--color-text-primary', '--color-text-secondary', '--color-metrics-text-tertiary', '--color-metrics-positive', '--color-metrics-negative', '--color-metrics-direction-neutral', '--color-metrics-unavailable-stroke', ...Array.from({ length: 7 }, (_, index) => `--color-metrics-kpi-${index + 1}`), ...['needs-you', 'blocked', 'stalled', 'over-budget', 'running', 'stale'].map((status) => `--color-metrics-status-${status}`), ...Array.from({ length: 5 }, (_, index) => `--color-metrics-grade-${index + 1}`)];
function RootThemeTokens() {
  useLayoutEffect(() => {
    const target = document.body;
    if (!target) return;
    const probe = document.createElement('span');
    target.append(probe);
    for (const token of themeTokens) {
      probe.style.color = metricsTokens[token as keyof typeof metricsTokens] ?? `var(${token})`;
      const colour = getComputedStyle(probe).color;
      if (colour) document.documentElement.style.setProperty(token, colour);
    }
    probe.remove();
  }, []);
  return null;
}
const router = makeRouter();

createRoot(root).render(
  <Theme theme={metricsTheme} mode="dark">
    <QueryClientProvider client={queryClient}>
    <RootThemeTokens />
      <style>{`.dashboard-shell :where(p,span,td,th,button,a){color:var(--color-text-primary)}.dashboard-shell [data-status-label]{background-color:var(--color-background-card);padding:2px}.dashboard-shell :is([data-status-icon],[data-status-count]){background-color:var(--color-text-primary);padding:2px}`}</style>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </Theme>,
);
