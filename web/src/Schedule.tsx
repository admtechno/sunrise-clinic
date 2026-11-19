// Session 06: the doctor's own appointments, with Complete for booked ones.
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
import ErrorAlert, { errorText } from "./ErrorAlert";
import { useCompleteAppointment, useSchedule } from "./hooks/useSchedule";

const colour = {
  booked: "primary",
  cancelled: "default",
  completed: "success",
} as const;

export default function Schedule() {
  const list = useSchedule(1);
  const complete = useCompleteAppointment();
  return (
    <Stack spacing={2}>
      <Typography variant="h5">My schedule</Typography>
      {complete.isError && (
        <Alert severity="error" onClose={() => complete.reset()}>
          Could not complete: {errorText(complete.error)}
        </Alert>
      )}
      {list.isPending && <CircularProgress aria-label="Loading schedule" />}
      {list.isError && <ErrorAlert error={list.error} />}
      {list.isSuccess && list.data.count === 0 && (
        <Typography>No appointments in your slots.</Typography>
      )}
      {list.isSuccess && list.data.count > 0 && (
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Date</TableCell>
              <TableCell>Time</TableCell>
              <TableCell>Patient</TableCell>
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
                <TableCell>{a.patient}</TableCell>
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
                      disabled={complete.isPending}
                      onClick={() => complete.mutate(a.id)}
                    >
                      Complete
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
