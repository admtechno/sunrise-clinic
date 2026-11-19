// Session 11, Demonstrations 1 and 2: the doctors list over the fake network.
// No vi.spyOn: the real client sends real fetch requests, and MSW answers them
// with the answers recorded from the API.
import { screen, waitFor } from "@testing-library/react";
import { expect, test } from "vitest";
import Doctors from "../../src/Doctors";
import { renderScreen } from "../render";
import { requestLog } from "../msw/server";

test("the rows come over the network", async () => {
  renderScreen(<Doctors />);
  const first = await screen.findByRole("cell", { name: "Dr. Arjun Nair" });
  expect(first).toBeInTheDocument();
  expect(screen.getByText("Page 1 of 3, 8 doctors")).toBeInTheDocument();
  expect(screen.getAllByRole("row")).toHaveLength(4); // the head, 3 doctors
});

test("the address becomes the query string the API receives", async () => {
  const log = requestLog();
  renderScreen(<Doctors />, { route: "/?speciality=paediatrics&ordering=-fee" });
  await screen.findByRole("cell", { name: "Dr. Arjun Nair" });
  // the handler does not filter: the test checks what was ASKED
  await waitFor(() => expect(log).toHaveLength(3));
  expect(log).toEqual([
    "GET /specialities/?page_size=20",
    "GET /doctors/?page=1&speciality=paediatrics&ordering=-fee&page_size=3",
    "GET /doctors/?page=2&speciality=paediatrics&ordering=-fee&page_size=3",
  ]); // the last one: the next page, asked for in advance (Session 07)
});
