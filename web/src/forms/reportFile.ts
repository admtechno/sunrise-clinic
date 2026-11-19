// Session 07: the checks the page makes BEFORE an upload. They only save the
// person a slow upload that is sure to fail; the API checks again, and also
// reads the first bytes of the file, which the page does not.
export const REPORT_TYPES = [".pdf", ".jpg", ".jpeg", ".png"];
export const REPORT_MAX_BYTES = 2 * 1024 * 1024; // the API's limit: 2 MB

export function checkReport(file: File): string | null {
  const dot = file.name.lastIndexOf(".");
  const type = dot >= 0 ? file.name.slice(dot).toLowerCase() : "";
  if (!REPORT_TYPES.includes(type)) return "Choose a PDF, JPG or PNG file.";
  if (file.size > REPORT_MAX_BYTES)
    return "This file is larger than 2 MB. Choose a smaller file.";
  return null; // nothing against it: send it
}
