// Session 11: one MSW server for every test file. It answers fetch requests in
// Node.js (no service worker): the handlers above, plus a test's own.
import { setupServer } from "msw/node";
import { handlers } from "./handlers";

export const server = setupServer(...handlers);

// every request the app sent in this test, as "GET /doctors/?page=1"
export function requestLog() {
  const log: string[] = [];
  server.events.on("request:start", ({ request }) => {
    const url = new URL(request.url);
    log.push(`${request.method} ${url.pathname.replace("/api/v1", "")}${url.search}`);
  });
  return log;
}
