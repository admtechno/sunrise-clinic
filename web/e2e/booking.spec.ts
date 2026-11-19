// Session 12: Asha books a visit, through the login
// page, the booking form and her list of appointments.
import { test, expect, login } from "./fixtures";

test("Asha books the 10:30 slot of Dr. Meera Shah", async ({ page }) => {
  await login(page, "asha");
  await page.goto("/doctors/1");
  await page.getByRole("combobox", { name: "Slot" }).click();
  await page.getByRole("option", { name: "2026-12-01 at 10:30" }).click();
  await page
    .getByRole("textbox", { name: "Reason for the visit" })
    .fill("Cough");
  await page.getByRole("button", { name: "Book" }).click();
  await expect(page.getByRole("alert")).toHaveText(
    "Booked: 2026-12-01 at 10:30, Dr. Meera Shah.",
  );
  // the slot is no longer free
  await expect(
    page.getByRole("listitem").filter({ hasText: "10:30" }),
  ).toHaveCount(0);

  await page.getByRole("link", { name: "My appointments" }).click();
  const row = page.getByRole("row").filter({ hasText: "Cough" });
  await expect(row).toContainText("10:30");
  await expect(row).toContainText("booked");
});
