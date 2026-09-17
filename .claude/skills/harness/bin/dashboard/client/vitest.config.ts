import { defineConfig } from "vitest/config";

export default defineConfig({
  cacheDir: process.env.VITEST_CACHE_DIR,
  test: {
    environment: "jsdom",
    globals: true,
    include: ["src/**/*.test.tsx"],
    setupFiles: ["./vitest.setup.ts"],
  },
});
