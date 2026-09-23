import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

vi.mock('@tanstack/react-router', () => ({ Link: ({ children }: { children: string }) => <a href="/work/example">{children}</a> }));

import { KpiPanel } from './panels';

const search = { window: 'all', repo: 'all' };
const gradingPayload = {
  aggregate: {
    grading: {
      bins: { '1': 2, '2': 1, '3': 0, '4': 3, '5': 1 },
      outliers: [{ qualname: 'needs_attention', path: 'src/example.py', line: 12, grade: 1, feature_id: 'FEAT-53' }],
      file_mix: { ungraded_files: 0, tracked_files: 7, ungraded_share: 0 },
    },
  },
  features: [{ feature_id: 'FEAT-53' }],
  trend: { records: {}, unavailable: {}, series: {}, weekly: { points: [], segments: [], unavailable: {} } },
};
const trendPayload = {
  aggregate: { throughput: { median_cycle_time_days: 4 }, touchpoints: { mean: 1 }, grading: { at_or_above_bar_share: 0.5 } },
  features: [{ feature_id: 'FEAT-53' }],
  trend: {
    records: {},
    unavailable: {},
    series: {
      cycle_time_days: { segments: [[{ at: '2026-09-01T00:00:00Z', value: 3, feature_id: 'FEAT-51' }], [{ at: '2026-09-15T00:00:00Z', value: 4, feature_id: 'FEAT-53' }]] },
      touchpoints: { segments: [[{ at: '2026-09-01T00:00:00Z', value: 1, feature_id: 'FEAT-51' }], [{ at: '2026-09-15T00:00:00Z', value: 2, feature_id: 'FEAT-53' }]] },
      grade: { segments: [[{ at: '2026-09-01T00:00:00Z', value: 0.4, feature_id: 'FEAT-51' }], [{ at: '2026-09-15T00:00:00Z', value: 0.5, feature_id: 'FEAT-53' }]] },
    },
    weekly: { points: [], segments: [], unavailable: {} },
  },
};
const mergedPayload = {
  aggregate: {},
  features: [{ feature_id: 'FEAT-53' }],
  trend: {
    records: {},
    unavailable: {},
    series: {},
    weekly: {
      points: [
        { week: '2026-09-01', value: 2 },
        { week: '2026-09-08', value: null, reason: 'no ship record in the week of 2026-09-08' },
        { week: '2026-09-15', value: 3 },
      ],
      segments: [
        [{ week: '2026-09-01', value: 2 }],
        [{ week: '2026-09-15', value: 3 }],
      ],
      week_count: 3,
      empty_bucket_count: 1,
      unavailable: {},
    },
  },
};

function expectShapeA(chart: HTMLElement) {
  expect(chart.querySelector('svg')).not.toBeNull();
  const labels = [...chart.querySelectorAll('*')].map((element) => element.textContent?.trim()).filter(Boolean);
  for (const label of ['Grade 1: 2', 'Grade 2: 1', 'Grade 3: 0', 'Grade 4: 3', 'Grade 5: 1']) expect(labels).toContain(label);
}

function expectShapeB(chart: HTMLElement, endLabel: string) {
  expect(chart.querySelector('svg')).not.toBeNull();
  expect(chart.querySelectorAll('svg path').length).toBeGreaterThanOrEqual(2);
  expect(chart.textContent).toContain(endLabel);
}

describe('KpiPanel chart mounts', () => {
  it('grading panel mounts the Shape A histogram', () => {
    render(<KpiPanel id={5} payload={gradingPayload} search={search} />);
    expectShapeA(screen.getByTestId('chart-shape-a'));
  });

  it('trend panel mounts the Shape B time series', () => {
    render(<KpiPanel id={1} payload={trendPayload} search={search} />);
    expectShapeB(screen.getByTestId('chart-shape-b'), 'Cycle time: 4');
  });

  it('merged PR panel mounts the Shape B weekly line', () => {
    render(<KpiPanel id={7} payload={mergedPayload} search={search} />);
    expectShapeB(screen.getByTestId('chart-shape-b'), 'Merged PRs: 3');
  });

  it('renders one disclosure with the tile definition for an unavailable KPI panel', () => {
    render(<KpiPanel id={3} payload={{ aggregate: { touchpoints: { mean: null, zero_count: 0, unavailable: { mean: 'no touchpoint records' } } }, features: [], trend: {} }} search={search} />);

    const disclosure = screen.getByRole('button', { name: 'About Blocking Human Touchpoints' });
    expect(screen.getAllByRole('button', { name: /About Blocking Human Touchpoints/ })).toHaveLength(1);
    fireEvent.click(disclosure);
    expect(screen.getByText('0 measured zero touchpoints')).toBeTruthy();
  });

  it('sums unattributed breakdown values for the KPI 6 panel without stringifying the breakdown', () => {
    render(<KpiPanel id={6} payload={{ aggregate: { attribution: { unattributed: { feature_only: 3, human: 5, no_prefix: 7, unresolvable_step_id: 11 }, total_commits: 40 } }, features: [], trend: {} }} search={search} />);

    expect(screen.getAllByText(/26 of 40 commits unattributed/)).not.toEqual([]);
    expect(screen.queryByText('[object Object]')).toBeNull();
  });
});
