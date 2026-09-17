import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { UnavailableValue } from './gapstates';

describe('UnavailableValue', () => {
  it('distinguishes an unavailable value from a measured zero', () => {
    render(<UnavailableValue reason="no ship record for this feature" />);

    expect(screen.getByText('—')).toBeTruthy();
    expect(screen.getByText('unavailable')).toBeTruthy();
    expect(screen.getByText('no ship record for this feature')).toBeTruthy();
    expect(screen.queryByText('0')).toBeNull();
  });
});
