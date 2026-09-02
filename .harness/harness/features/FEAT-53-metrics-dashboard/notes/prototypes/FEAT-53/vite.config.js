import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';

// Prototype only. SPA fallback (vite's default appType) is what makes
// /features/$featureId reloadable and pasteable — SC-11's hand test.
export default defineConfig({
  plugins: [react()],
  server: {port: 5273, strictPort: true},
});
