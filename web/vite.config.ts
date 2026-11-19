/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    // While you develop, a request from the page to /api/... is passed on to
    // the Django API on port 8000. The browser only ever talks to the Vite
    // address, so there is one origin and no CORS check.
    proxy: { "/api": "http://127.0.0.1:8000" },
  },
  // Session 14: `npm run build` writes dist; `vite preview` serves dist the
  // way a host would, and passes /api on with the same proxy as above.
  build: { sourcemap: false }, // the default, written down: no source maps
  preview: { host: "127.0.0.1", port: 4173, strictPort: true },
  // Session 10: component tests; Session 11: tests over a fake network. Vitest uses this file too, so the tests see
  // the same plugins as the app. jsdom is a browser made of JavaScript: a
  // document, elements and events, but no screen and no network.
  test: {
    environment: "jsdom",
    setupFiles: ["./test/setup.ts"],
    include: ["test/components/**/*.test.tsx", "test/network/**/*.test.tsx"],
  },
});
