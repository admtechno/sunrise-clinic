// Route guards: layout routes that decide whether the screens below them are
// shown. They spare the person a screen that would only fail; they do not
// protect anything. The API answers 401 or 403 whatever the page shows.
import { Alert, CircularProgress, Stack, Typography } from "@mui/material";
import { Navigate, Outlet, useLocation } from "react-router";
import { useAuth } from "./AuthProvider";
import { roleName, type Role } from "./roles.ts";

// Needs a logged-in person. A visitor goes to /login, which remembers where
// they wanted to go; after Log out the person goes home. While the session is
// being restored, wait.
export function RequireAuth() {
  const { status, loggedOut } = useAuth();
  const location = useLocation();
  if (status === "restoring") {
    return (
      <Stack direction="row" spacing={2} sx={{ alignItems: "center" }}>
        <CircularProgress size={24} />
        <Typography>Checking your login...</Typography>
      </Stack>
    );
  }
  if (status !== "signedIn" && loggedOut) {
    return <Navigate to="/" replace />; // after Log out: home, not the login
  }
  if (status !== "signedIn") {
    const from = location.pathname + location.search; // /schedule?page=2
    return <Navigate to="/login" replace state={{ from }} />;
  }
  return <Outlet />;
}

// Needs one of the roles. Another role sees a clear message, not the login page
// (they are logged in) and not a blank page.
export function RequireRole({ roles }: { roles: Role[] }) {
  const { me } = useAuth();
  if (me && roles.includes(me.role as Role)) {
    return <Outlet />;
  }
  const who = roles.map((r) => roleName[r]).join(" or ");
  return (
    <Alert severity="warning">
      This page is for {who} logins. You are logged in as {me?.username}.
    </Alert>
  );
}
