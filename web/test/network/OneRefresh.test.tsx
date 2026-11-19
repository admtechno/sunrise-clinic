// Session 11, Mini Challenge: two requests find an expired token at the same
// moment. The API accepts each refresh token once, so the app must ask for a
// new access token ONCE, and both requests must then go through.
import { http, HttpResponse } from "msw";
import { expect, test } from "vitest";
import { api } from "../../src/api";
import { setToken } from "../../src/auth/tokenStore";
import { API, apiError, meAsAsha } from "../msw/handlers";
import { server } from "../msw/server";

test("two expired requests share one refresh", async () => {
  let refreshes = 0;
  const fresh = (request: Request) =>
    request.headers.get("Authorization") === "Bearer new-token";
  server.use(
    http.post(`${API}/auth/cookie/refresh/`, () => {
      refreshes += 1;
      return HttpResponse.json({ access: "new-token" });
    }),
    http.get(`${API}/me/`, ({ request }) => fresh(request) ? undefined
      : apiError(401, "token_not_valid", "Token is invalid or expired")),
    meAsAsha, // answers /me/ when the handler above returns nothing
    http.get(`${API}/appointments/`, ({ request }) => fresh(request)
      ? HttpResponse.json({ count: 0, next: null, previous: null, results: [] })
      : apiError(401, "token_not_valid", "Token is invalid or expired")),
  );
  setToken("old-token"); // signed in a while ago; the token has expired
  const [me, page] = await Promise.all([api.me(), api.listAppointments()]);
  expect(me.username).toBe("asha");
  expect(page.count).toBe(0);
  expect(refreshes).toBe(1);
});
