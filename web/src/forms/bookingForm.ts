// The booking form, checked in the browser before anything is sent. The API
// checks the same rules again: the browser check is for speed, the API check is
// the one that counts.
import { z } from "zod";

export const bookingFormSchema = z.object({
  slot: z.number({ error: "Choose a free slot." }).int().positive(),
  reason: z
    .string()
    .trim()
    .max(200, "Keep the reason to 200 characters or fewer."),
});

export type BookingForm = z.infer<typeof bookingFormSchema>;
