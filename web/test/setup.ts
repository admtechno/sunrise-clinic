// Session 10 and 11: runs before every component test file.
import "@testing-library/jest-dom/vitest"; // toBeInTheDocument(), toHaveValue() ...
import { cleanup } from "@testing-library/react";
import { afterAll, afterEach, beforeAll, vi } from "vitest";
import { setToken } from "../src/auth/tokenStore";
import { server } from "./msw/server";

// a request without a handler fails the test (no real network, ever)
beforeAll(() => server.listen({ onUnhandledFrame: "error" }));
afterEach(() => {
  cleanup(); // remove what the test rendered
  server.resetHandlers(); // forget the handlers one test added
  server.events.removeAllListeners(); // and its request log
  setToken(null); // the token store is a module variable: nobody signed in
  vi.restoreAllMocks(); // undo every vi.spyOn of the test
});
afterAll(() => server.close());
