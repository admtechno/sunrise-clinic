// Session 10: render a screen with what it needs around it: a fresh
// TanStack Query cache (no retries, so a failure shows at once) and a router
// at the given address. The user object of user-event types and clicks.
// Session 11: { auth: true } adds the AuthProvider (it asks the refresh cookie,
// so the handlers decide who is signed in); { retry } sets the query retries.
import type { ReactElement } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router";
import { AuthProvider } from "../src/auth/AuthProvider";

interface Options {
  route?: string;
  path?: string; // a route pattern such as "/doctors/:id"
  auth?: boolean;
  retry?: boolean | ((count: number, error: Error) => boolean);
}

export function renderScreen(ui: ReactElement, options: Options = {}) {
  const { route = "/", path, auth = false, retry = false } = options;
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry, retryDelay: 0 },
      mutations: { retry: false },
    },
  });
  const user = userEvent.setup();
  const screen = path ? <Routes><Route path={path} element={ui} /></Routes> : ui;
  const result = render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[route]}>
        {auth ? <AuthProvider>{screen}</AuthProvider> : screen}
      </MemoryRouter>
    </QueryClientProvider>,
  );
  return { user, queryClient, ...result };
}
