// Session 10, Demonstration 5: the states of a list. Each test decides what
// the API answers (vi.spyOn) and checks what the person sees: a spinner, an
// empty list, an error with a button, and the rows.
import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, test, vi } from "vitest";
import Doctors from "../../src/Doctors";
import { api, ApiError, type Doctor, type DoctorPage } from "../../src/api";
import { renderScreen } from "../render";

const GM = { id: 1, name: "General Medicine", slug: "general-medicine" };
const doctor = (id: number, name: string, fee: string): Doctor =>
  ({ id, name, speciality: GM, fee, bio: "", is_active: true });
const page = (results: Doctor[], count = results.length): DoctorPage =>
  ({ count, next: null, previous: null, results });
const MEERA = doctor(1, "Dr. Meera Shah", "500.00");
const ARJUN = doctor(2, "Dr. Arjun Patel", "600.00");
const cell = (name: string) => screen.findByRole("cell", { name });

beforeEach(() => {
  vi.spyOn(api, "listSpecialities").mockResolvedValue([GM]);
});

describe("the doctors list", () => {
  test("shows a spinner until the answer arrives, then the rows", async () => {
    vi.spyOn(api, "listDoctors").mockResolvedValue(page([MEERA, ARJUN]));
    renderScreen(<Doctors />);
    const spinner = screen.getByRole("progressbar", { name: "Loading doctors" });
    expect(spinner).toBeInTheDocument();
    expect(await cell("Dr. Meera Shah")).toBeInTheDocument();
    expect(screen.getAllByRole("row")).toHaveLength(3); // the head, 2 doctors
    expect(screen.queryByRole("progressbar")).not.toBeInTheDocument();
  });

  test("an empty answer says that nothing matches", async () => {
    vi.spyOn(api, "listDoctors").mockResolvedValue(page([]));
    renderScreen(<Doctors />, { route: "/?search=zzz" });
    const none = await screen.findByText("No doctors match your filters.");
    expect(none).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  test("an error offers Try again, which asks again", async () => {
    const list = vi.spyOn(api, "listDoctors")
      .mockRejectedValueOnce(new ApiError({
        status: 500, code: "SERVER_ERROR", message: "The API had a problem.",
      }))
      .mockResolvedValueOnce(page([MEERA]));
    const { user } = renderScreen(<Doctors />);
    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Could not load the doctors (SERVER_ERROR)");
    await user.click(screen.getByRole("button", { name: "Try again" }));
    expect(await cell("Dr. Meera Shah")).toBeInTheDocument();
    expect(list).toHaveBeenCalledTimes(2);
  });

  test("the address decides what is asked for", async () => {
    const list = vi.spyOn(api, "listDoctors").mockResolvedValue(page([]));
    const route = "/?speciality=general-medicine&ordering=-fee";
    renderScreen(<Doctors />, { route });
    await screen.findByText("No doctors match your filters.");
    expect(list).toHaveBeenCalledWith({
      page: 1, search: undefined, speciality: "general-medicine",
      ordering: "-fee", page_size: 3,
    });
  });
});
