// Who is signed in, for every screen: useAuth(). On start the provider tries
// the refresh cookie once (session restore), so a reload keeps you signed in.
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  useSyncExternalStore,
} from "react";
import { useQueryClient } from "@tanstack/react-query";
import { api, type Me } from "../api";
import { refreshOnce } from "./refresh.ts";
import { currentToken, setToken, subscribe } from "./tokenStore.ts";

interface AuthValue {
  status: "restoring" | "signedOut" | "signedIn";
  me: Me | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  // Session 06: true after Log out (the guards then send the person home, not
  // to the login page)
  loggedOut: boolean;
}

const AuthContext = createContext<AuthValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const token = useSyncExternalStore(subscribe, currentToken);
  const [me, setMe] = useState<Me | null>(null);
  const [restoring, setRestoring] = useState(true);
  const [loggedOut, setLoggedOut] = useState(false);
  const queryClient = useQueryClient();

  useEffect(() => {
    // StrictMode runs this twice in development; refreshOnce shares one request
    let live = true;
    refreshOnce()
      .then(async (access) => {
        if (access && live) setMe(await api.me());
      })
      .catch(() => setToken(null))
      .finally(() => live && setRestoring(false));
    return () => {
      live = false;
    };
  }, []);

  useEffect(() => {
    if (token === null) {
      setMe(null); // signed out or the session ended
      // not for the next person at the desk
      queryClient.removeQueries({ queryKey: ["appointments"] });
      queryClient.removeQueries({ queryKey: ["schedule"] });
      queryClient.removeQueries({ queryKey: ["reports"] }); // Session 07
    }
  }, [token, queryClient]);

  const login = useCallback(async (username: string, password: string) => {
    const { access } = await api.login(username, password);
    setLoggedOut(false);
    setToken(access);
    setMe(await api.me());
  }, []);

  const logout = useCallback(async () => {
    try {
      await api.logout(); // the API forgets the refresh token
    } finally {
      setLoggedOut(true);
      setToken(null);
    }
  }, []);

  const status = restoring
    ? "restoring"
    : token && me
      ? "signedIn"
      : "signedOut";
  return (
    <AuthContext
      value={{ status, me: token ? me : null, login, logout, loggedOut }}
    >
      {children}
    </AuthContext>
  );
}

export function useAuth(): AuthValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside <AuthProvider>");
  return value;
}
