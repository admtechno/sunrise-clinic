// The shapes the client accepts. zod checks every answer against them, and the
// TypeScript types come from the same schemas.
import { z } from "zod";

export const specialitySchema = z.object({
  id: z.number().int(),
  name: z.string(),
  slug: z.string(),
});

export const doctorSchema = z.object({
  id: z.number().int(),
  name: z.string(),
  speciality: specialitySchema,
  // Django sends a decimal as text
  fee: z.string().regex(/^\d+\.\d{2}$/, "a fee such as 600.00"),
  bio: z.string(),
  is_active: z.boolean(),
});

// A free slot of one doctor (GET /doctors/<id>/slots/).
export const slotSchema = z.object({
  id: z.number().int(),
  doctor: z.number().int(),
  doctor_name: z.string(),
  date: z.iso.date(), // "2026-12-01"
  start_time: z.string().regex(/^\d{2}:\d{2}$/, "a time such as 10:30"),
});

// Every list of the API has this shape (Django REST Framework page-number
// pagination).
export const pageOf = <T extends z.ZodType>(item: T) =>
  z.object({
    count: z.number().int(),
    next: z.url().nullable(),
    previous: z.url().nullable(),
    results: z.array(item),
  });

export const doctorPageSchema = pageOf(doctorSchema);
export const specialityPageSchema = pageOf(specialitySchema);

// The error body of the API (Django course, Session 16).
export const errorBodySchema = z.object({
  error: z.object({
    status: z.number().int(),
    code: z.string(),
    message: z.string(),
    fields: z.record(z.string(), z.array(z.string())).optional(),
  }),
});

// A slot as reception sees it (GET /slots/): it also says whether it is booked.
export const managedSlotSchema = slotSchema.extend({ booked: z.boolean() });
export const managedSlotPageSchema = pageOf(managedSlotSchema);

// An appointment (GET /appointments/ and the answer of every booking change).
// The slot comes nested, so one request is enough for a row of the table.
export const appointmentSchema = z.object({
  id: z.number().int(),
  slot: z.object({
    id: z.number().int(),
    doctor: z.string(), // the doctor's name
    date: z.iso.date(),
    start_time: z.string().regex(/^\d{2}:\d{2}$/),
  }),
  patient: z.string(),
  status: z.enum(["booked", "cancelled", "completed"]),
  reason: z.string(),
  created_at: z.iso.datetime({ offset: true }),
});
export const appointmentPageSchema = pageOf(appointmentSchema);

// Session 05: the answer of the cookie login and refresh (the refresh token is
// in the cookie, not here).
export const accessSchema = z.object({ access: z.string() });
export const meSchema = z.object({
  username: z.string(),
  role: z.string(),
  groups: z.array(z.string()),
  is_patient: z.boolean(),
});

// Session 07: a report file of an appointment (GET and POST
// /appointments/<id>/reports/). The stored path is never sent.
export const reportSchema = z.object({
  id: z.number().int(),
  original_name: z.string(),
  size: z.number().int(),
  uploaded_at: z.iso.datetime({ offset: true }),
});

export type Speciality = z.infer<typeof specialitySchema>;
export type Doctor = z.infer<typeof doctorSchema>;
export type Slot = z.infer<typeof slotSchema>;
export type DoctorPage = z.infer<typeof doctorPageSchema>;
export type ManagedSlot = z.infer<typeof managedSlotSchema>;
export type ManagedSlotPage = z.infer<typeof managedSlotPageSchema>;
export type Appointment = z.infer<typeof appointmentSchema>;
export type AppointmentPage = z.infer<typeof appointmentPageSchema>;
export type Me = z.infer<typeof meSchema>;
export type Report = z.infer<typeof reportSchema>;
