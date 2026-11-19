// Session 06: addresses for the screens. Session 07 adds the reports. Public
// screens are open to everyone; the others sit inside the guards. The menu
// shows what the role may use. Session 14: the screens of a logged-in role
// are loaded only when someone opens them (lazy): a visitor never gets them.
import {
  AppBar,
  Button,
  CircularProgress,
  Container,
  Toolbar,
  Typography,
} from "@mui/material";
import { lazy, Suspense } from "react";
import { Link, Route, Routes } from "react-router";
import { useAuth } from "./auth/AuthProvider";
import { RequireAuth, RequireRole } from "./auth/guards";
import { isRole, menu, roleName } from "./auth/roles.ts";
import DoctorDetail from "./DoctorDetail";
import Doctors from "./Doctors";
import Login from "./Login";

// each import() becomes a file of its own in dist/assets
const MyAppointments = lazy(() => import("./MyAppointments"));
const AppointmentReports = lazy(() => import("./AppointmentReports"));
const Schedule = lazy(() => import("./Schedule"));
const Slots = lazy(() => import("./Slots"));

export default function App() {
  const { status, me, logout } = useAuth();
  const role = me && isRole(me.role) ? me.role : null;
  return (
    <>
      <AppBar position="static">
        <Toolbar sx={{ gap: 1 }}>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Sunrise Clinic Desk
          </Typography>
          <Button color="inherit" component={Link} to="/">
            Doctors
          </Button>
          {role &&
            menu[role].map((item) => (
              <Button
                key={item.to}
                color="inherit"
                component={Link}
                to={item.to}
              >
                {item.label}
              </Button>
            ))}
          {status === "signedIn" && me && (
            <>
              <Typography sx={{ ml: 2 }}>
                {me.username} ({role ? roleName[role] : me.role})
              </Typography>
              <Button
                color="inherit"
                onClick={() => void logout()} // the guard sends you home
              >
                Log out
              </Button>
            </>
          )}
          {status === "signedOut" && (
            <Button color="inherit" component={Link} to="/login">
              Log in
            </Button>
          )}
        </Toolbar>
      </AppBar>
      <Container sx={{ py: 3 }}>
        {/* shown for the moment a screen's file is on its way */}
        <Suspense fallback={<CircularProgress aria-label="Loading screen" />}>
          <Routes>
            <Route path="/" element={<Doctors />} />
            <Route path="/doctors/:id" element={<DoctorDetail />} />
            <Route path="/login" element={<Login />} />
            <Route element={<RequireAuth />}>
              <Route element={<RequireRole roles={["patient"]} />}>
                <Route path="/appointments" element={<MyAppointments />} />
              </Route>
              <Route element={<RequireRole roles={["patient", "doctor"]} />}>
                <Route
                  path="/appointments/:id/reports"
                  element={<AppointmentReports />}
                />
              </Route>
              <Route element={<RequireRole roles={["doctor"]} />}>
                <Route path="/schedule" element={<Schedule />} />
              </Route>
              <Route element={<RequireRole roles={["admin"]} />}>
                <Route path="/reception/slots" element={<Slots />} />
              </Route>
            </Route>
          </Routes>
        </Suspense>
      </Container>
    </>
  );
}
