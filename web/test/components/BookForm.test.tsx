// Session 10, Demonstrations 2 to 4: the booking form as a person uses it.
// The network is not used: vi.spyOn replaces api.bookAppointment for one test
// and says what it answers. (Session 11 fakes the network itself instead.)
import { screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import BookForm from "../../src/BookForm";
import { api, ApiError, type Appointment, type Slot } from "../../src/api";
import { renderScreen } from "../render";

const slot = (id: number, start_time: string): Slot => ({
  id, doctor: 1, doctor_name: "Dr. Meera Shah", date: "2026-12-01", start_time,
});
const SLOTS = [slot(1, "10:00"), slot(2, "10:30")];
const BOOKED: Appointment = {
  id: 7,
  slot: { id: 2, doctor: "Dr. Meera Shah", date: "2026-12-01", start_time: "10:30" },
  patient: "Asha Verma",
  status: "booked",
  reason: "Fever",
  created_at: "2026-11-17T09:00:00Z",
};

// the three things a person uses, found by role and name
const slotField = () => screen.getByRole("combobox", { name: "Slot" });
const reasonBox = () =>
  screen.getByRole("textbox", { name: "Reason for the visit" });
const bookButton = () => screen.getByRole("button", { name: "Book" });

function renderForm() {
  const view = renderScreen(<BookForm doctorId={1} slots={SLOTS} />);
  const chooseSlot = async (label: string) => {
    await view.user.click(slotField()); // MUI opens a list of options
    await view.user.click(screen.getByRole("option", { name: label }));
  };
  return { ...view, chooseSlot };
}

describe("BookForm", () => {
  test("the form has a slot, a reason and a Book button", () => {
    renderForm();
    expect(slotField()).toBeInTheDocument();
    expect(reasonBox()).toHaveValue("");
    expect(bookButton()).toBeEnabled();
  });

  test("without a slot nothing is sent, and the slot says why", async () => {
    const book = vi.spyOn(api, "bookAppointment");
    const { user } = renderForm();
    await user.click(bookButton());
    expect(screen.getByText("Choose a free slot.")).toBeInTheDocument();
    expect(book).not.toHaveBeenCalled();
  });

  test("a booking sends the slot and the reason, then says so", async () => {
    const book = vi.spyOn(api, "bookAppointment").mockResolvedValue(BOOKED);
    const { user, chooseSlot } = renderForm();
    await chooseSlot("2026-12-01 at 10:30");
    await user.type(reasonBox(), "Fever");
    await user.click(bookButton());
    expect(book).toHaveBeenCalledWith({ slot: 2, reason: "Fever" });
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Booked: 2026-12-01 at 10:30, Dr. Meera Shah.",
    );
    expect(reasonBox()).toHaveValue("");
  });

  test("the API's 400 is shown beside the slot", async () => {
    vi.spyOn(api, "bookAppointment").mockRejectedValue(
      new ApiError({
        status: 400, code: "invalid", message: "Some fields are not valid.",
        fields: { slot: ["This time slot is already booked."] },
      }),
    );
    const { user, chooseSlot } = renderForm();
    await chooseSlot("2026-12-01 at 10:00");
    await user.click(bookButton());
    const error = await screen.findByText("This time slot is already booked.");
    expect(error).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument(); // no form line
  });

  test("an answer that is not a field error is shown above the button", async () => {
    vi.spyOn(api, "bookAppointment").mockRejectedValue(
      new ApiError({
        status: 0, code: "NETWORK_ERROR", message: "The API cannot be reached.",
      }),
    );
    const { user, chooseSlot } = renderForm();
    await chooseSlot("2026-12-01 at 10:00");
    await user.click(bookButton());
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "The API cannot be reached.",
    );
  });
});
