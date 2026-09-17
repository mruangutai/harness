import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createMemoryHistory, RouterProvider } from '@tanstack/react-router';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { makeRouter, productPaths } from './routes';

const kpis = { kpis: Array.from({ length: 7 }, (_, index) => ({ id: index + 1, label: `KPI ${index + 1}` })) };

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
    ['/kpi/1', 'KPI 1'],
    ['/work/FEAT-1', 'Example Feature'],
  ])('renders %s', async (path, expected) => {
    vi.stubGlobal('fetch', vi.fn((input: URL | RequestInfo) => {
      const url = String(input);
      return Promise.resolve(new Response(JSON.stringify(url.includes('/api/kpis') ? kpis : work)));
    }));

    renderRoute(path);
    expect(await screen.findByRole('heading', { name: expected })).toBeTruthy();
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
    fireEvent.click(await screen.findByRole('link', { name: 'KPI 1' }));

    await waitFor(() => expect(history.location.href).toBe('/kpi/1?window=90d&repo=alpha'));
    renderRoute(history.location.href);
    await screen.findAllByRole('heading', { name: 'KPI 1' });

    const requested = fetchMock.mock.calls.map(([input]) => String(input));
    expect(requested).toContain('/api/kpis?window=90d&repo=alpha');
    expect(requested).toContain('/api/work?window=90d&repo=alpha');
  });
});
