import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createMemoryHistory, RouterProvider } from '@tanstack/react-router';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { makeRouter, productPaths } from './routes';

const kpis = {
  features: [{ feature_id: 'FEAT-1', name: 'Example Feature' }],
  aggregate: {
    escaped_defects: {
      count: 1,
      sourcing_rule: 'BUG units and default-branch reverts in the selected window.',
      items: [{ feature_id: 'BUG-1', name: 'Escaped defect' }],
    },
  },
  trend: { weekly: { week_count: 1, empty_bucket_count: 0 } },
};

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});
const work = { items: [{ id: 'FEAT-1', kind: 'FEAT', name: 'Example Feature' }] };

function renderRoute(initialEntry: string) {
  const history = createMemoryHistory({ initialEntries: [initialEntry] });
  const router = makeRouter({ history });
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  render(
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  );
  return { history, router };
}

afterEach(() => vi.unstubAllGlobals());

describe('dashboard product routes', () => {
  it.each([
    ['/', 'Operations Dashboard'],
    ['/kpi/1', 'Throughput'],
    ['/work/FEAT-1', 'Example Feature'],
  ])('renders %s', async (path, expected) => {
    vi.stubGlobal('fetch', vi.fn((input: URL | RequestInfo) => {
      const url = String(input);
      return Promise.resolve(new Response(JSON.stringify(url.includes('/api/kpis') ? kpis : work)));
    }));

    renderRoute(path);
    expect((await screen.findAllByRole('heading', { name: expected })).length).toBeGreaterThan(0);
  });

  it('registers only the three product paths', () => {
    expect(productPaths).toEqual(['/', '/kpi/$n', '/work/$id']);
  });

  it.each(['/work', '/features', '/features/FEAT-1', '/kpis', '/kpis/1'])('does not register retired path %s', async (path) => {
    vi.stubGlobal('fetch', vi.fn());
    const { router } = renderRoute(path);
    await router.load();
    expect(router.state.matches.some((match) => match.routeId !== '__root__')).toBe(false);
  });

  it('keeps URL-owned window and repository state across requests, routes, and reload', async () => {
    const fetchMock = vi.fn((input: URL | RequestInfo) => {
      const url = String(input);
      return Promise.resolve(new Response(JSON.stringify(url.includes('/api/kpis') ? kpis : work)));
    });
    vi.stubGlobal('fetch', fetchMock);

    const { history } = renderRoute('/?window=30d&repo=alpha');
    await screen.findByRole('heading', { name: 'Operations Dashboard' });
    fireEvent.click(screen.getByRole('radio', { name: '90d' }));
    fireEvent.click(await screen.findByRole('link', { name: 'Throughput' }));

    await waitFor(() => expect(history.location.href).toBe('/kpi/1?window=90d&repo=alpha'));
    renderRoute(history.location.href);
    await screen.findAllByRole('heading', { name: 'Throughput' });

    const requested = fetchMock.mock.calls.map(([input]) => String(input));
    expect(requested).toContain('/api/kpis?window=90d&repo=alpha');
    expect(requested).toContain('/api/work?window=90d&repo=alpha');
  });

  it('keeps the available dashboard region usable when the other query fails', async () => {
    vi.stubGlobal('fetch', vi.fn((input: URL | RequestInfo) => {
      const url = String(input);
      return url.includes('/api/kpis')
        ? Promise.reject(new Error('KPI source unavailable'))
        : Promise.resolve(new Response(JSON.stringify(work)));
    }));

    renderRoute('/');

    expect(await screen.findByRole('heading', { name: 'Repository KPIs unavailable' })).toBeTruthy();
    expect(screen.getByText('KPI source unavailable')).toBeTruthy();
    expect(await screen.findByRole('heading', { name: 'Work List' })).toBeTruthy();
    expect(await screen.findByText('Example Feature')).toBeTruthy();
  });

  it('keeps settled KPI content usable when the work request fails', async () => {
    vi.stubGlobal('fetch', vi.fn((input: URL | RequestInfo) => {
      if (String(input).includes('/api/kpis')) return Promise.resolve(new Response(JSON.stringify(kpis)));
      return Promise.reject(new Error('Work source unavailable'));
    }));

    renderRoute('/');

    expect(await screen.findByRole('heading', { name: 'Repository KPIs' })).toBeTruthy();
    expect(screen.getByRole('link', { name: 'Escaped Defects' })).toBeTruthy();
    expect(await screen.findByRole('heading', { name: 'Work list unavailable' })).toBeTruthy();
    expect(screen.getByText('Work source unavailable')).toBeTruthy();
  });

  it('renders a complete KPI panel and lands focus after an in-app KPI transition', async () => {
    const detailedKpis = {
      features: [{ feature_id: 'BUG-1', name: 'Escaped defect' }],
      aggregate: {
        escaped_defects: {
          count: 1,
          sourcing_rule: 'BUG units and default-branch reverts in the selected window.',
          items: [{ feature_id: 'BUG-1', name: 'Escaped defect' }],
        },
      },
      trend: { weekly: { week_count: 1, empty_bucket_count: 0 } },
    };
    vi.stubGlobal('fetch', vi.fn((input: URL | RequestInfo) => Promise.resolve(new Response(JSON.stringify(
      String(input).includes('/api/kpis') ? detailedKpis : work,
    )))));

    renderRoute('/');
    fireEvent.click(await screen.findByRole('link', { name: 'Escaped Defects' }));

    const title = await screen.findByRole('heading', { name: 'Escaped Defects', level: 1 });
    expect(title.getAttribute('tabindex')).toBe('-1');
    await waitFor(() => expect(document.activeElement).toBe(title));
    expect(screen.getByRole('button', { name: 'About Escaped Defects' })).toBeTruthy();
    expect(screen.getByRole('link', { name: 'BUG-1' }).getAttribute('href')).toContain('/work/BUG-1');
  });

});
