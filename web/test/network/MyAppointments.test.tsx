// Session 11, Do It Yourself: Asha's appointments over the fake network: the
// rows, an empty list, and a cancel that the API refuses (the row comes back).
import { screen, within } from "@testing-library/react";
import { delay, http, HttpResponse } from "msw";
import { expect, test } from "vitest";
import MyAppointments from "../../src/MyAppointments";
import { renderScreen } from "../render";
import { API, apiError, bookedAnswer, signedInAsAsha } from "../msw/handlers";
import { server } from "../msw/server";

const page = (results: unknown[]) =>
  ({ count: results.length, next: null, previous: null, results });
const ASHA = bookedAnswer(2, "Fever"); // booked, 2026-12-01 at 10:30

test("Asha sees her appointment", async () => {
  server.use(...signedInAsAsha,
    http.get(`${API}/appointments/`, () => HttpResponse.json(page([ASHA]))));
  renderScreen(<MyAppointments />, { auth: true });
  const row = (await screen.findByRole("cell", { name: "Fever" })).closest("tr")!;
  expect(within(row).getByText("Dr. Meera Shah")).toBeInTheDocument();
  expect(within(row).getByText("booked")).toBeInTheDocument();
});

test("no appointments yet", async () => {
  server.use(...signedInAsAsha,
    http.get(`${API}/appointments/`, () => HttpResponse.json(page([]))));
  renderScreen(<MyAppointments />, { auth: true });
  expect(await screen.findByText("No appointments yet.")).toBeInTheDocument();
});

test("a cancel the API refuses puts the row back", async () => {
  server.use(...signedInAsAsha,
    http.get(`${API}/appointments/`, () => HttpResponse.json(page([ASHA]))),
    http.post(`${API}/appointments/7/cancel/`, async () => {
      await delay(200); // long enough to see the optimistic row
      return apiError(400, "invalid", "Too late to cancel this visit.");
    }));
  const { user } = renderScreen(<MyAppointments />, { auth: true });
  await user.click(await screen.findByRole("button", { name: "Cancel" }));
  expect(await screen.findByText("cancelled")).toBeInTheDocument(); // at once
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "Could not cancel: Too late to cancel this visit.");
  expect(screen.getByText("booked")).toBeInTheDocument(); // rolled back
});
