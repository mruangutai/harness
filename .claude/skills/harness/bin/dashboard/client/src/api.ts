export type SharedSearch = { window: string; repo: string };

function query(search: SharedSearch): string {
  return new URLSearchParams({ window: search.window, repo: search.repo }).toString();
}

async function request<T>(path: string, search: SharedSearch): Promise<T> {
  const response = await fetch(`${path}?${query(search)}`);
  if (!response.ok) throw new Error(`Dashboard request failed: ${response.status}`);
  return response.json() as Promise<T>;
}

export function fetchKpis(search: SharedSearch) {
  return request<{ kpis: Array<{ id: number; label: string }> }>('/api/kpis', search);
}

export function fetchWork(search: SharedSearch) {
  return request<{ items: Array<{ id: string; kind: string; name: string }> }>('/api/work', search);
}
