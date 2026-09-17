import { defineTheme } from '@astryxdesign/core';
import { neutralTheme } from '@astryxdesign/theme-neutral';

export const metricsTheme = defineTheme({
  name: 'metrics-dashboard',
  extends: neutralTheme,
  tokens: {
    '--color-metrics-text-tertiary': '#8A95A3',
    '--color-metrics-positive': '#4ADE9B',
    '--color-metrics-negative': '#FF8172',
    '--color-metrics-direction-neutral': '#94A0AE',
    '--color-metrics-kpi-1': '#A78BFA',
    '--color-metrics-kpi-2': '#78A9FF',
    '--color-metrics-kpi-3': '#3FD0B8',
    '--color-metrics-kpi-4': '#F58BC2',
    '--color-metrics-kpi-5': '#E8B45A',
    '--color-metrics-kpi-6': '#C6D96B',
    '--color-metrics-kpi-7': '#49B9EA',
    '--color-metrics-status-needs-you': '#F8C15C',
    '--color-metrics-status-blocked': '#FF8172',
    '--color-metrics-status-stalled': '#D6A7FF',
    '--color-metrics-status-over-budget': '#F58BC2',
    '--color-metrics-status-running': '#4ADE9B',
    '--color-metrics-status-stale': '#8A95A3',
    '--color-metrics-grade-1': '#FF8A80',
    '--color-metrics-grade-2': '#E0A33A',
    '--color-metrics-grade-3': '#9AA4B2',
    '--color-metrics-grade-4': '#3FC98A',
    '--color-metrics-grade-5': '#86F0BE',
    '--color-metrics-unavailable-stroke': '#7A8492',
  },
});
