// Query keys: one place that says how cached answers are named. A key lists
// everything the answer depends on. A different key is a different cache entry.
import type { DoctorQuery } from "./client.ts";

export const doctorKeys = {
  all: ["doctors"] as const,
  list: (query: DoctorQuery) => ["doctors", "list", query] as const,
  detail: (id: number) => ["doctors", "detail", id] as const,
  slots: (id: number) => ["doctors", "slots", id] as const,
};

export const specialityKeys = {
  all: ["specialities"] as const,
};

// Session 04: the appointments of the signed-in person, and the slots reception
// manages.
export const appointmentKeys = {
  all: ["appointments"] as const,
  list: (page: number) => ["appointments", "list", page] as const,
};

export const slotKeys = {
  all: ["slots"] as const,
  list: (query: object) => ["slots", "list", query] as const,
};

// Session 06: the doctor's schedule
export const scheduleKeys = {
  all: ["schedule"] as const,
  list: (page: number) => ["schedule", "list", page] as const,
};

// Session 07: the reports of one appointment
export const reportKeys = {
  list: (appointmentId: number) => ["reports", appointmentId] as const,
};
