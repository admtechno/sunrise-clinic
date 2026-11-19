// One error type for everything that can go wrong when the page talks to the
// API. It is built from the error shape of the Sunrise Clinic API: { error: {
// status, code, message, fields? } }.
export type FieldErrors = Record<string, string[]>;

export interface ApiErrorInit {
  status: number;
  code: string;
  message: string;
  fields?: FieldErrors;
}

export class ApiError extends Error {
  status: number; // the HTTP status, or 0 when no answer arrived at all
  // a short name such as not_found, invalid, not_authenticated or NETWORK_ERROR
  code: string;
  // one list of messages per invalid field (400 answers); empty otherwise
  fields: FieldErrors;

  constructor(init: ApiErrorInit) {
    super(init.message);
    this.name = "ApiError";
    this.status = init.status;
    this.code = init.code;
    this.fields = init.fields ?? {};
  }
}
