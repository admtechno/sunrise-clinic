// The appointments of the signed-in patient, with an optimistic Cancel.
import {
  Alert,
  Button,
  Chip,
  CircularProgress,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { Link } from "react-router";
import { useAuth } from "./auth/AuthProvider";
import {
  useCancelAppointment,
  useMyAppointments,
} from "./hooks/useAppointments";

const colour = {
  booked: "primary",
  cancelled: "default",
  completed: "success",
} as const;

export default function MyAppointments() {
  const { me } = useAuth();
  const list = useMyAppointments(1, Boolean(me));
  const cancel = useCancelAppointment();

  if (!me) return <Typography>Log in to see your appointments.</Typography>;
  return (
    <Stack spacing={2}>
      <Typography variant="h5">My appointments</Typography>
      {cancel.isError && (
        <Alert severity="error" onClose={() => cancel.reset()}>
          Could not cancel: {cancel.error.message}
        </Alert>
      )}
      {list.isPending && <CircularProgress aria-label="Loading appointments" />}
      {list.isError && <Alert severity="error">{list.error.message}</Alert>}
      {list.isSuccess && list.data.count === 0 && (
        <Typography>No appointments yet.</Typography>
      )}
      {list.isSuccess && list.data.count > 0 && (
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Time</TableCell>
              <TableCell>Doctor</TableCell>
              <TableCell>Reason</TableCell>
              <TableCell>Status</TableCell>
              <TableCell />
            </TableRow>
          </TableHead>
          <TableBody>
            {list.data.results.map((a) => (
              <TableRow key={a.id}>
                <TableCell>{a.slot.date}</TableCell>
                <TableCell>{a.slot.start_time}</TableCell>
                <TableCell>{a.slot.doctor}</TableCell>
                <TableCell>{a.reason || "-"}</TableCell>
                <TableCell>
                  <Chip
                    size="small"
                    label={a.status}
                    color={colour[a.status]}
                  />
                </TableCell>
                <TableCell>
                  <Button
                    size="small"
                    component={Link}
                    to={`/appointments/${a.id}/reports`}
                  >
                    Reports
                  </Button>
                  {a.status === "booked" && (
                    <Button
                      size="small"
                      disabled={cancel.isPending && cancel.variables === a.id}
                      onClick={() => cancel.mutate(a.id)}
                    >
                      Cancel
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </Stack>
  );
}
