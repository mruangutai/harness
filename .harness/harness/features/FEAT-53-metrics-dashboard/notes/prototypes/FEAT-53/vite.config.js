import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';

// Prototype only. Vite's SPA fallback keeps every approved route reloadable.
export default defineConfig({
  plugins: [react()],
  server: {port: 5273, strictPort: true},
});
