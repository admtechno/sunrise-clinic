// Asks the API for a new access token with the refresh cookie. Several requests
// can find an expired token at the same moment; they all wait for ONE refresh,
// because the API accepts each refresh token only once.
import { createClient } from "../api/client.ts";
import { API_BASE_URL } from "../api/config.ts";
import { setToken } from "./tokenStore.ts";

// a client without a token and without repair, for the cookie calls
const cookieApi = createClient({ baseUrl: API_BASE_URL });
let running: Promise<string | null> | null = null;

// one refresh request; the new token goes into the store, or null when the
// session has ended (no cookie, or the refresh token was refused)
export function startRefresh(): Promise<string | null> {
  return cookieApi.refreshAccess().then(
    ({ access }) => {
      setToken(access);
      return access;
    },
    () => {
      setToken(null);
      return null;
    },
  );
}

export function refreshOnce(): Promise<string | null> {
  running ??= startRefresh().finally(() => {
    running = null;
  });
  return running; // a caller that comes while it runs joins the same request
}
