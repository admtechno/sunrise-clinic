// Reception adds and deletes the slots of a doctor (the screen of the DIY and
// mini challenge of Session 04). The API's 400 field errors appear beside Date
// and Time; an error about the whole slot appears above the button.
import { useState } from "react";
import {
  Alert,
  Button,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { fromApiError, noErrors } from "./forms/fieldErrors";
import { useDoctorList } from "./hooks/useDoctors";
import { useCreateSlot, useDeleteSlot, useDoctorSlots } from "./hooks/useSlots";

export default function Slots() {
  const doctors = useDoctorList({ page_size: 20, ordering: "name" });
  const [doctor, setDoctor] = useState(1);
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [errors, setErrors] = useState(noErrors);
  const slots = useDoctorSlots(doctor);
  const create = useCreateSlot();
  const remove = useDeleteSlot();

  function submit(event: React.FormEvent) {
    event.preventDefault();
    setErrors(noErrors);
    create.mutate(
      { doctor, date, start_time: time },
      {
        onSuccess: () => setTime(""),
        onError: (e) => setErrors(fromApiError(e, ["date", "start_time"])),
      },
    );
  }

  return (
    <Stack spacing={2}>
      <Typography variant="h5">Slots</Typography>
      <TextField
        select
        label="Doctor"
        // Session 13: no value until the doctors are there (MUI warned in
        // the browser tests that 1 was not one of the options yet)
        value={doctors.isSuccess ? doctor : ""}
        onChange={(e) => setDoctor(Number(e.target.value))}
        sx={{ width: 320 }}
      >
        {(doctors.data?.results ?? []).map((d) => (
          <MenuItem key={d.id} value={d.id}>
            {d.name}
          </MenuItem>
        ))}
      </TextField>
      <Stack component="form" direction="row" spacing={2} onSubmit={submit}>
        <TextField
          label="Date"
          placeholder="2026-12-03"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          error={Boolean(errors.fields.date)}
          helperText={errors.fields.date ?? " "}
        />
        <TextField
          label="Time"
          placeholder="09:30"
          value={time}
          onChange={(e) => setTime(e.target.value)}
          error={Boolean(errors.fields.start_time)}
          helperText={errors.fields.start_time ?? " "}
        />
        <Button type="submit" variant="contained" disabled={create.isPending}>
          Add slot
        </Button>
      </Stack>
      {errors.form && <Alert severity="error">{errors.form}</Alert>}
      {remove.isError && (
        <Alert severity="error" onClose={() => remove.reset()}>
          Could not delete: {remove.error.message}
        </Alert>
      )}
      {slots.isSuccess && (
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Id</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Time</TableCell>
              <TableCell>Booked</TableCell>
              <TableCell />
            </TableRow>
          </TableHead>
          <TableBody>
            {slots.data.results.map((s) => (
              <TableRow key={s.id}>
                <TableCell>{s.id}</TableCell>
                <TableCell>{s.date}</TableCell>
                <TableCell>{s.start_time}</TableCell>
                <TableCell>{s.booked ? "yes" : "no"}</TableCell>
                <TableCell>
                  <Button
                    size="small"
                    color="error"
                    disabled={remove.isPending}
                    onClick={() => remove.mutate(s)}
                  >
                    Delete
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </Stack>
  );
}
