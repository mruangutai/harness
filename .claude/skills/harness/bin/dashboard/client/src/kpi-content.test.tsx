import { fireEvent, render, screen, within } from '@testing-library/react';
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
  trend: { weekly: { week_count: 4, empty_bucket_count: 1, unavailable: {}, sourcing_rule: 'KPI 7 test sentinel: weekly counts come from the supplied dashboard payload.' } },
};

describe('KpiTiles', () => {
  it('renders the seven KPI links and keeps measured zero distinct from unavailable', () => {
    render(<KpiTiles payload={payload} search={{ window: 'all', repo: 'all' }} />);

    expect(screen.getAllByRole('link')).toHaveLength(7);
    expect(screen.getAllByText('0').length).toBeGreaterThan(0);
    expect(screen.queryByText('unavailable')).toBeNull();
    fireEvent.click(screen.getByRole('button', { name: 'About Merged PRs Over Time' }));
    expect(screen.getByText('KPI 7 test sentinel: weekly counts come from the supplied dashboard payload.')).toBeTruthy();
  });

  it('sums unattributed breakdown values for the KPI 6 tile without stringifying the breakdown', () => {
    render(<KpiTiles payload={{ ...payload, aggregate: { ...payload.aggregate, attribution: { attributable_share: 0.5, unattributed: { feature_only: 3, human: 5, no_prefix: 7, unresolvable_step_id: 11 }, total_commits: 40, unavailable: {} } } }} search={{ window: 'all', repo: 'all' }} />);

    expect(screen.getAllByText('26 of 40 commits unattributed')).not.toEqual([]);
    expect(screen.queryByText('[object Object]')).toBeNull();
  });

  it('renders Throughput as unavailable when zero measured features carry an exclusion reason', () => {
    render(<KpiTiles payload={{ ...payload, aggregate: { ...payload.aggregate, throughput: { median_cycle_time_days: 0, measured_features: 0, unavailable: { excluded_features: '91 features lack a ship record or approval date' } } } }} search={{ window: 'all', repo: 'all' }} />);

    expect(screen.getByText('91 features lack a ship record or approval date')).toBeTruthy();
    const throughputTile = screen.getByRole('link', { name: 'Throughput' }).closest('[data-elevation]');
    expect(within(throughputTile!).queryByText('0')).toBeNull();
  });
});
