// Session 11, Demonstration 3: every way an answer can go wrong, one test each.
// server.use() puts a handler in front of the shared ones for this test only.
import { screen } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { describe, expect, test } from "vitest";
import Doctors from "../../src/Doctors";
import BookForm from "../../src/BookForm";
import type { Slot } from "../../src/api";
import { renderScreen } from "../render";
import { API, apiError } from "../msw/handlers";
import { server } from "../msw/server";
import page1 from "../msw/recorded/doctors_page1.json";

const wrongShape = { ...page1, results: [{ ...page1.results[0], fee: 650 }] };
const ANSWERS = [
  ["a 500 with the error body", "SERVER_ERROR",
    () => apiError(500, "SERVER_ERROR", "The API had a problem.")],
  ["a 502 page that is not JSON", "HTTP_502",
    () => new HttpResponse("<h1>Bad Gateway</h1>", { status: 502 })],
  ["no answer at all", "NETWORK_ERROR", () => HttpResponse.error()],
  ["a 200 of the wrong shape", "UNEXPECTED_RESPONSE",
    () => HttpResponse.json(wrongShape)], // fee 650 instead of "650.00"
] as const;

describe("the doctors list when the answer goes wrong", () => {
  test.each(ANSWERS)("%s", async (_name, code, answer) => {
    server.use(http.get(`${API}/doctors/`, answer));
    renderScreen(<Doctors />);
    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(`Could not load the doctors (${code})`);
  });
});

const SLOTS: Slot[] = [{
  id: 2, doctor: 1, doctor_name: "Dr. Meera Shah",
  date: "2026-12-01", start_time: "10:30",
}];

test("the API's 400 for a booking reaches the slot field", async () => {
  server.use(http.post(`${API}/appointments/`, () =>
    apiError(400, "invalid", "Some fields are not valid.",
      { slot: ["This time slot is already booked."] })));
  const { user } = renderScreen(<BookForm doctorId={1} slots={SLOTS} />);
  await user.click(screen.getByRole("combobox", { name: "Slot" }));
  await user.click(screen.getByRole("option", { name: "2026-12-01 at 10:30" }));
  await user.click(screen.getByRole("button", { name: "Book" }));
  const error = await screen.findByText("This time slot is already booked.");
  expect(error).toBeInTheDocument();
});
