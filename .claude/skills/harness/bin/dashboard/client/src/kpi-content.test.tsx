import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
vi.mock('@tanstack/react-router', () => ({ Link: ({ children }: { children: string }) => <a href="/kpi/">{children}</a> }));
import { KpiTiles } from './tiles';

const payload = {
  aggregate: {
    throughput: { median_cycle_time_days: 4, measured_features: 2, unavailable: {} },
    rework: { cycles_used: 2, max_total_cycles: 4, unavailable: {} },
    touchpoints: { mean: 0, zero_count: 2, unavailable: {} },
    escaped_defects: { count: 0, unavailable: {}, sourcing_rule: 'A source rule.' },
    grading: { at_or_above_share: 0.5, unavailable: {} },
    attribution: { attributable_share: 0.5, unattributed: 2, total_commits: 4, unavailable: {} },
  },
  trend: { weekly: { week_count: 4, empty_bucket_count: 1, unavailable: {}, sourcing_rule: 'Weekly counts are shipped features read from the durable ship record; each shipped feature represents one merged PR under DEC-200; nullable pr fields do not affect the count.' } },
};

describe('KpiTiles', () => {
  it('renders the seven KPI links and keeps measured zero distinct from unavailable', () => {
    render(<KpiTiles payload={payload} search={{ window: 'all', repo: 'all' }} />);

    expect(screen.getAllByRole('link')).toHaveLength(7);
    expect(screen.getAllByText('0').length).toBeGreaterThan(0);
    expect(screen.queryByText('unavailable')).toBeNull();
    expect(screen.getByRole('button', { name: 'About Merged PRs Over Time' })).toBeTruthy();
  });
});
