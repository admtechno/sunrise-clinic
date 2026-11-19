// Mini challenge: Asha and Ravi want the same slot, each in a browser of
// their own. Asha books first; Ravi's page still offers the slot.
import { test, expect, login } from "./fixtures";

test("the second patient finds the slot taken", async ({ page, browser }) => {
  const ravisBrowser = await browser.newContext(); // own cookies, own login
  const ravi = await ravisBrowser.newPage();
  await login(page, "asha");
  await login(ravi, "ravi");
  for (const p of [page, ravi]) {
    await p.goto("/doctors/1");
    await p.getByRole("combobox", { name: "Slot" }).click();
    await p.getByRole("option", { name: "2026-12-01 at 10:30" }).click();
    await p
      .getByRole("textbox", { name: "Reason for the visit" })
      .fill("Cough");
  }
  await page.getByRole("button", { name: "Book" }).click();
  await expect(page.getByRole("alert")).toContainText("Booked:");

  await ravi.getByRole("button", { name: "Book" }).click();
  await expect(
    ravi.getByText("This time slot is already booked."),
  ).toBeVisible();
  await expect(ravi.getByRole("combobox", { name: "Slot" })).toHaveAttribute(
    "aria-invalid",
    "true",
  );
  // the list of free slots was asked again: 10:30 is gone for Ravi too
  await expect(
    ravi.getByRole("listitem").filter({ hasText: "10:30" }),
  ).toHaveCount(0);
  await ravisBrowser.close();
});
