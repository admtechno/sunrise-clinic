// Book one of the free slots of a doctor. Two layers of checks: zod in the
// browser first, then the API, whose 400 field errors are shown beside the same
// fields.
import { useRef, useState } from "react";
import { Alert, Button, MenuItem, Stack, TextField } from "@mui/material";
import type { Slot } from "./api";
import { bookingFormSchema } from "./forms/bookingForm";
import { fromApiError, fromZodError, noErrors } from "./forms/fieldErrors";
import { useBookAppointment } from "./hooks/useAppointments";

interface Props {
  doctorId: number;
  slots: Slot[];
}

export default function BookForm({ doctorId, slots }: Props) {
  const book = useBookAppointment(doctorId);
  const [slot, setSlot] = useState<number | "">("");
  const [reason, setReason] = useState("");
  const [errors, setErrors] = useState(noErrors);
  const [booked, setBooked] = useState<string | null>(null);
  // true from the first click until the answer: a second click in the same
  // moment sees it at once (isPending only changes after the next render)
  const sending = useRef(false);

  function submit(event: React.FormEvent) {
    event.preventDefault();
    if (sending.current) return; // a double click
    setBooked(null);
    const input = { slot: slot === "" ? undefined : slot, reason };
    const checked = bookingFormSchema.safeParse(input);
    if (!checked.success) {
      setErrors(fromZodError(checked.error)); // layer 1: nothing is sent
      return;
    }
    setErrors(noErrors);
    sending.current = true;
    book.mutate(checked.data, {
      onSuccess: (a) => {
        setBooked(
          `Booked: ${a.slot.date} at ${a.slot.start_time}, ${a.slot.doctor}.`,
        );
        setSlot("");
        setReason("");
      },
      onError: (error) => {
        setErrors(fromApiError(error, ["slot", "reason"])); // layer 2
        setSlot(""); // the chosen slot may be gone
      },
      onSettled: () => {
        sending.current = false;
      },
    });
  }

  return (
    <Stack component="form" spacing={2} onSubmit={submit} sx={{ width: 520 }}>
      <TextField
        select
        label="Slot"
        value={slot}
        onChange={(e) => setSlot(Number(e.target.value))}
        error={Boolean(errors.fields.slot)}
        helperText={errors.fields.slot ?? " "}
      >
        {slots.map((s) => (
          <MenuItem key={s.id} value={s.id}>
            {s.date} at {s.start_time}
          </MenuItem>
        ))}
      </TextField>
      <TextField
        label="Reason for the visit"
        value={reason}
        onChange={(e) => setReason(e.target.value)}
        error={Boolean(errors.fields.reason)}
        helperText={errors.fields.reason ?? `${reason.length}/200`}
        multiline
      />
      {errors.form && <Alert severity="error">{errors.form}</Alert>}
      {booked && <Alert severity="success">{booked}</Alert>}
      <Button
        type="submit"
        variant="contained"
        disabled={book.isPending}
        sx={{ alignSelf: "flex-start" }}
      >
        {book.isPending ? "Booking..." : "Book"}
      </Button>
    </Stack>
  );
}
