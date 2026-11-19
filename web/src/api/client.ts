// The only place in the Clinic Desk that calls fetch. Screens call the typed
// functions at the bottom.
import { z } from "zod";
import { ApiError } from "./errors.ts";
import {
  accessSchema,
  appointmentPageSchema,
  appointmentSchema,
  doctorPageSchema,
  doctorSchema,
  errorBodySchema,
  managedSlotPageSchema,
  meSchema,
  reportSchema,
  slotSchema,
  specialityPageSchema,
} from "./schemas.ts";
import type {
  Appointment,
  AppointmentPage,
  Doctor,
  DoctorPage,
  ManagedSlotPage,
  Me,
  Report,
  Slot,
  Speciality,
} from "./schemas.ts";

export interface ClientOptions {
  // for example "/api/v1" in the browser, "http://127.0.0.1:8000/api/v1" in a
  // script
  baseUrl: string;
  fetch?: typeof fetch; // a script may give its own fetch
  // the access token to send, or null when nobody is signed in
  getToken?: () => string | null;
  // Session 05: asked for a new access token when the API says that ours has
  // expired; resolves to the new token, or null when the session has ended
  refreshToken?: () => Promise<string | null>;
}

type QueryValue = string | number | boolean | undefined;

export interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  query?: Record<string, QueryValue>;
  body?: unknown;
  headers?: Record<string, string>;
  auth?: false; // Session 05: no Bearer token and no repair (the cookie calls)
  // Session 07: a file upload. The browser writes the Content-Type itself, with
  // the boundary that separates the parts.
  form?: FormData;
  onProgress?: (percent: number) => void; // how much of the upload has left
}

// Session 05: the cookie views of the API want this header on every request; a
// form on another site cannot send it.
const CLIENT_HEADER = { "X-Clinic-Client": "desk" };

export interface DoctorQuery {
  page?: number;
  page_size?: number; // the API allows at most 20
  search?: string;
  speciality?: string; // a slug such as "paediatrics"
  max_fee?: number;
  ordering?: "name" | "-name" | "fee" | "-fee";
}

// What the page sends to book a slot (POST /appointments/).
export interface BookingInput {
  slot: number;
  reason: string;
}

// What reception sends to create or change a slot (POST and PATCH /slots/).
export interface SlotInput {
  doctor: number;
  date: string; // "2026-12-03"
  start_time: string; // "09:30"
}

export function buildQuery(query: Record<string, QueryValue> = {}): string {
  const params = new URLSearchParams();
  for (const [name, value] of Object.entries(query)) {
    if (value !== undefined && value !== "") params.set(name, String(value));
  }
  const text = params.toString();
  return text ? `?${text}` : "";
}

export function createClient(options: ClientOptions) {
  const baseUrl = options.baseUrl.replace(/\/+$/, "");
  // Session 11: look up fetch at each request, not once here. A test tool such
  // as MSW replaces the global fetch after this module has been loaded.
  const doFetch: typeof fetch =
    options.fetch ?? ((input, init) => fetch(input, init));

  // Session 05: one repair. An expired access token gets a 401 with the code
  // token_not_valid; ask for a new token once, then send the request again.
  async function request<T>(
    path: string,
    schema: z.ZodType<T>,
    init: RequestOptions = {},
  ): Promise<T> {
    try {
      return await send(path, schema, init);
    } catch (error) {
      const expired =
        error instanceof ApiError &&
        error.status === 401 &&
        error.code === "token_not_valid";
      if (!expired || init.auth === false || !options.refreshToken) throw error;
      const fresh = await options.refreshToken();
      if (!fresh) throw error; // the session has ended
      return send(path, schema, init); // once: a second 401 is final
    }
  }

  async function send<T>(
    path: string,
    schema: z.ZodType<T>,
    init: RequestOptions,
  ): Promise<T> {
    const url = `${baseUrl}${path}${buildQuery(init.query)}`;
    const headers: Record<string, string> = {
      Accept: "application/json",
      ...init.headers,
    };
    if (init.body !== undefined) headers["Content-Type"] = "application/json";
    const token = init.auth === false ? null : options.getToken?.();
    if (token) headers.Authorization = `Bearer ${token}`;

    let answer: { status: number; text: string };
    try {
      if (init.form && init.onProgress && typeof XMLHttpRequest !== "undefined")
        answer = await sendWithProgress(
          url,
          headers,
          init.form,
          init.onProgress,
        );
      else {
        const response = await doFetch(url, {
          method: init.method ?? "GET",
          headers,
          body:
            init.form ??
            (init.body === undefined ? undefined : JSON.stringify(init.body)),
        });
        answer = { status: response.status, text: await response.text() };
      }
    } catch {
      throw new ApiError({
        status: 0,
        code: "NETWORK_ERROR",
        message: "The API could not be reached",
      });
    }
    return finish(answer.status, answer.text, schema);
  }

  function finish<T>(status: number, text: string, schema: z.ZodType<T>): T {
    // 204 No Content (a DELETE that worked) has no body to parse
    if (status === 204) return schema.parse(undefined);

    let json: unknown;
    try {
      json = JSON.parse(text);
    } catch {
      // not JSON: for example Django's HTML page for an unknown address
      json = undefined;
    }

    if (status < 200 || status > 299) {
      const parsed = errorBodySchema.safeParse(json);
      if (parsed.success) {
        const { code, message, fields } = parsed.data.error;
        throw new ApiError({ status, code, message, fields });
      }
      throw new ApiError({
        status,
        code: `HTTP_${status}`,
        message: `The API answered ${status}`,
      });
    }

    const result = schema.safeParse(json);
    if (!result.success) {
      const fields: Record<string, string[]> = {};
      for (const issue of result.error.issues)
        (fields[issue.path.join(".")] ??= []).push(issue.message);
      throw new ApiError({
        status,
        code: "UNEXPECTED_RESPONSE",
        message: "The API answer does not have the expected shape",
        fields,
      });
    }
    return result.data;
  }

  return {
    request,
    listSpecialities: (): Promise<Speciality[]> =>
      request("/specialities/", specialityPageSchema, {
        query: { page_size: 20 },
      }).then((page) => page.results),
    listDoctors: (query: DoctorQuery = {}): Promise<DoctorPage> =>
      request("/doctors/", doctorPageSchema, { query: { ...query } }),
    getDoctor: (id: number): Promise<Doctor> =>
      request(`/doctors/${id}/`, doctorSchema),
    getFreeSlots: (doctorId: number): Promise<Slot[]> =>
      request(`/doctors/${doctorId}/slots/`, z.array(slotSchema)),

    // Session 05: the browser login. The refresh token travels only in the
    // HttpOnly cookie; the answers carry the access token.
    login: (username: string, password: string) =>
      request("/auth/cookie/login/", accessSchema, {
        method: "POST",
        body: { username, password },
        headers: CLIENT_HEADER,
        auth: false,
      }),
    refreshAccess: () =>
      request("/auth/cookie/refresh/", accessSchema, {
        method: "POST",
        headers: CLIENT_HEADER,
        auth: false,
      }),
    logout: (): Promise<void> =>
      request("/auth/cookie/logout/", z.undefined(), {
        method: "POST",
        headers: CLIENT_HEADER,
        auth: false,
      }),
    me: (): Promise<Me> => request("/me/", meSchema),

    // Session 04: the calls that change data.
    bookAppointment: (input: BookingInput): Promise<Appointment> =>
      request("/appointments/", appointmentSchema, {
        method: "POST",
        body: input,
      }),
    listAppointments: (page = 1): Promise<AppointmentPage> =>
      request("/appointments/", appointmentPageSchema, { query: { page } }),
    // Session 07: one appointment (its patient, its doctor, or staff)
    getAppointment: (id: number): Promise<Appointment> =>
      request(`/appointments/${id}/`, appointmentSchema),
    // Session 06: the logged-in doctor's appointments (doctors only)
    getSchedule: (page = 1): Promise<AppointmentPage> =>
      request("/doctor/schedule/", appointmentPageSchema, { query: { page } }),
    cancelAppointment: (id: number): Promise<Appointment> =>
      request(`/appointments/${id}/cancel/`, appointmentSchema, {
        method: "POST",
      }),
    completeAppointment: (id: number): Promise<Appointment> =>
      request(`/appointments/${id}/complete/`, appointmentSchema, {
        method: "POST",
      }),
    listSlots: (
      query: {
        doctor?: number;
        date?: string;
        page?: number;
        page_size?: number;
      } = {},
    ): Promise<ManagedSlotPage> =>
      request("/slots/", managedSlotPageSchema, { query: { ...query } }),
    // The answer to a POST has no "booked" field (only lists say it), so the
    // write calls check it with slotSchema (found by demonstration 1).
    createSlot: (input: SlotInput): Promise<Slot> =>
      request("/slots/", slotSchema, { method: "POST", body: input }),
    updateSlot: (id: number, change: Partial<SlotInput>): Promise<Slot> =>
      request(`/slots/${id}/`, slotSchema, {
        method: "PATCH",
        body: change,
      }),
    deleteSlot: (id: number): Promise<void> =>
      request(`/slots/${id}/`, z.undefined(), { method: "DELETE" }),

    // Session 07: the reports of one appointment, and the upload of one file.
    listReports: (appointmentId: number): Promise<Report[]> =>
      request(`/appointments/${appointmentId}/reports/`, z.array(reportSchema)),
    uploadReport: (
      appointmentId: number,
      file: Blob,
      fileName: string,
      onProgress?: (percent: number) => void,
    ): Promise<Report> => {
      const form = new FormData();
      form.append("file", file, fileName); // "file": the name the API reads
      return request(`/appointments/${appointmentId}/reports/`, reportSchema, {
        method: "POST",
        form,
        onProgress,
      });
    },
  };
}

export type ApiClient = ReturnType<typeof createClient>;

// Session 07: fetch cannot report how much of a request body has been sent, so
// an upload with a progress bar uses the older XMLHttpRequest. Only the browser
// has it; scripts and tests upload with fetch.
function sendWithProgress(
  url: string,
  headers: Record<string, string>,
  form: FormData,
  onProgress: (percent: number) => void,
): Promise<{ status: number; text: string }> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", url);
    for (const [name, value] of Object.entries(headers))
      xhr.setRequestHeader(name, value);
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable)
        onProgress(Math.round((event.loaded / event.total) * 100));
    };
    xhr.onload = () => resolve({ status: xhr.status, text: xhr.responseText });
    xhr.onerror = () => reject(new Error("network"));
    xhr.send(form);
  });
}
