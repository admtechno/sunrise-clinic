// Session 07: the doctors list lives in the address, for example
// /?speciality=general-medicine&ordering=-fee&page=2. Anybody can type anything
// there, so every value is checked, and a value that does not fit becomes the
// default.
import { z } from "zod";
import type { DoctorQuery } from "../api";

export const PAGE_SIZE = 3;
export const ORDERINGS = ["name", "-name", "fee", "-fee"] as const;

const searchSchema = z.object({
  page: z.coerce.number().int().min(1).catch(1),
  search: z.string().trim().min(1).max(60).optional().catch(undefined),
  // the slugs come from the API, so only their form is checked here
  speciality: z
    .string()
    .regex(/^[a-z0-9-]{1,50}$/)
    .optional()
    .catch(undefined),
  ordering: z.enum(ORDERINGS).catch("name"),
});
export type DoctorSearch = z.infer<typeof searchSchema>;

const NAMES = ["page", "search", "speciality", "ordering"] as const;

export function readSearch(params: URLSearchParams): DoctorSearch {
  const raw = Object.fromEntries(
    NAMES.map((name) => [name, params.get(name) || undefined]),
  );
  return searchSchema.parse(raw);
}

// The address keeps only what differs from the defaults, so "/" stays "/".
export function writeSearch(search: DoctorSearch): URLSearchParams {
  const params = new URLSearchParams();
  if (search.speciality) params.set("speciality", search.speciality);
  if (search.search) params.set("search", search.search);
  if (search.ordering !== "name") params.set("ordering", search.ordering);
  if (search.page !== 1) params.set("page", String(search.page));
  return params;
}

export function toQuery(search: DoctorSearch): DoctorQuery {
  return { ...search, page_size: PAGE_SIZE };
}
