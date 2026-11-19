// Turns an error into what a form shows: one message beside each field it
// knows, and one message for the whole form (everything else).
import { z } from "zod";
import { ApiError } from "../api";

export interface FormErrors {
  fields: Record<string, string>; // field name -> message beside the field
  form: string | null; // the message above the button
}

export const noErrors: FormErrors = { fields: {}, form: null };

// A 400 from the API: { error: { fields: { slot: ["..."], ... } } }
export function fromApiError(error: unknown, known: string[]): FormErrors {
  if (!(error instanceof ApiError)) return { fields: {}, form: String(error) };
  const fields: Record<string, string> = {};
  const other: string[] = [];
  for (const [name, messages] of Object.entries(error.fields)) {
    if (known.includes(name)) fields[name] = messages.join(" ");
    else other.push(...messages); // for example non_field_errors
  }
  const form = other.length ? other.join(" ") : error.message;
  // a field error explains itself; keep the form line for anything else
  return {
    fields,
    form: Object.keys(fields).length && !other.length ? null : form,
  };
}

// The browser check: the same zod issues, shaped like the API's answer.
export function fromZodError(error: z.ZodError): FormErrors {
  const fields: Record<string, string> = {};
  for (const issue of error.issues)
    fields[String(issue.path[0])] ??= issue.message;
  return { fields, form: null };
}
