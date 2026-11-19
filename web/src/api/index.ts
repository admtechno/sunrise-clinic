// The one client the screens use. It sends the access token from the token
// store and, when the API says the token has expired, asks for a new one once.
import { createClient } from "./client.ts";
import { API_BASE_URL } from "./config.ts";
import { currentToken } from "../auth/tokenStore.ts";
import { refreshOnce } from "../auth/refresh.ts";

export const api = createClient({
  baseUrl: API_BASE_URL,
  getToken: currentToken,
  refreshToken: refreshOnce,
});
export { ApiError } from "./errors.ts";
export type {
  Appointment,
  AppointmentPage,
  Doctor,
  DoctorPage,
  ManagedSlot,
  ManagedSlotPage,
  Me,
  Report,
  Slot,
  Speciality,
} from "./schemas.ts";
export type { BookingInput, DoctorQuery, SlotInput } from "./client.ts";
