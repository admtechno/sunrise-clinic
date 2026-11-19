// One way to show an API error on a screen. 401 and 403 get words for the
// person; everything else shows the API's own message.
import { Alert } from "@mui/material";
import { ApiError } from "./api";

export function errorText(error: Error): string {
  if (error instanceof ApiError && error.status === 403) {
    return `Your login may not do this. The API says: ${error.message}`;
  }
  if (error instanceof ApiError && error.status === 401) {
    return "Your session has ended. Please log in again.";
  }
  return error.message;
}

export default function ErrorAlert({ error }: { error: Error }) {
  return <Alert severity="error">{errorText(error)}</Alert>;
}
