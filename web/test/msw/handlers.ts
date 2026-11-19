// Session 11: the fake network of the tests. Each handler answers one address
// of the API with an answer recorded from the real API (tools/record_answers.mjs)
// or built in its shape. A test changes one answer with server.use(...).
import { http, HttpResponse } from "msw";
import { API_BASE_URL as API } from "../../src/api/config";
import specialities from "./recorded/specialities.json";
import page1 from "./recorded/doctors_page1.json";
import page2 from "./recorded/doctors_page2.json";
import doctor1 from "./recorded/doctor_1.json";
import slots1 from "./recorded/doctor_1_slots.json";

export { API };

// the error body of the API (api/exceptions.py)
export const apiError = (
  status: number, code: string, message: string,
  fields?: Record<string, string[]>,
) => HttpResponse.json(
  { error: { status, code, message, ...(fields ? { fields } : {}) } }, { status },
);

export const handlers = [
  http.get(`${API}/specialities/`, () => HttpResponse.json(specialities)),
  http.get(`${API}/doctors/`, ({ request }) => {
    const page = new URL(request.url).searchParams.get("page");
    return HttpResponse.json(page === "2" ? page2 : page1);
  }),
  http.get(`${API}/doctors/:id/`, ({ params }) =>
    params.id === "1" ? HttpResponse.json(doctor1)
      : apiError(404, "not_found", "No Doctor matches the given query.")),
  http.get(`${API}/doctors/:id/slots/`, () => HttpResponse.json(slots1)),
  // nobody is signed in: the refresh cookie is missing
  http.post(`${API}/auth/cookie/refresh/`, () =>
    apiError(401, "not_authenticated", "No refresh cookie.")),
];

// Asha is signed in: the refresh cookie gives an access token, /me/ says who.
export const meAsAsha = http.get(`${API}/me/`, () => HttpResponse.json({
  username: "asha", role: "patient", groups: ["Patients"], is_patient: true,
}));
export const signedInAsAsha = [
  http.post(`${API}/auth/cookie/refresh/`, () =>
    HttpResponse.json({ access: "test-access-1" })),
  meAsAsha,
];

// The answer of a booking, in the shape of the API, for the slot that was sent.
export function bookedAnswer(slotId: number, reason: string) {
  const slot = slots1.find((s) => s.id === slotId)!;
  return {
    id: 7, patient: "Asha Verma", status: "booked", reason,
    slot: { id: slot.id, doctor: slot.doctor_name, date: slot.date,
      start_time: slot.start_time },
    created_at: "2026-11-17T09:00:00+05:30",
  };
}
