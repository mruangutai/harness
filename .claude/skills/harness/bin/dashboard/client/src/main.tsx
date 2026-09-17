import '@astryxdesign/core/reset.css';
import '@astryxdesign/core/astryx.css';
import '@astryxdesign/theme-neutral/theme.css';

import { Theme } from '@astryxdesign/core';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider } from '@tanstack/react-router';
import { createRoot } from 'react-dom/client';
import { makeRouter } from './routes';
import { metricsTheme } from './theme';

const root = document.getElementById('root');
if (!root) throw new Error('Missing dashboard root');

const queryClient = new QueryClient({ defaultOptions: { queries: { refetchInterval: false } } });
const router = makeRouter();

createRoot(root).render(
  <Theme theme={metricsTheme} mode="dark">
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </Theme>,
);
