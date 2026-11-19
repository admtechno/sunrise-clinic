// The roles of the Sunrise Clinic API (User.role) and what each one finds in
// the menu. A menu is a convenience for the person; the API decides what is
// allowed. Reception staff have the role "admin" and the group Reception.
export type Role = "patient" | "doctor" | "admin";

export const roleName: Record<Role, string> = {
  patient: "patient",
  doctor: "doctor",
  admin: "reception",
};

export const menu: Record<Role, { to: string; label: string }[]> = {
  patient: [{ to: "/appointments", label: "My appointments" }],
  doctor: [{ to: "/schedule", label: "My schedule" }],
  admin: [{ to: "/reception/slots", label: "Slots" }],
};

export const isRole = (value: string): value is Role => value in menu;

// Session 07: what each role may do with the reports of an appointment. The API
// has the same rules (ReportRules); these only decide what is shown.
export const canUploadReports = (role: Role | null) => role === "patient";
export const canReadReports = (role: Role | null) =>
  role === "patient" || role === "doctor";
