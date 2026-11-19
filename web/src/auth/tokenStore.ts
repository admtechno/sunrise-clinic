// The access token, in memory only: a module variable. It is lost when the page
// reloads (the refresh cookie brings it back), and it is never written to
// localStorage, where any script on the page could read it.
let token: string | null = null;
const listeners = new Set<() => void>();

export const currentToken = () => token;

export function setToken(next: string | null) {
  token = next;
  listeners.forEach((listener) => listener());
}

// for React's useSyncExternalStore
export function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}
