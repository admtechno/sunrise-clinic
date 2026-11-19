// Mini challenge: Asha books, Dr. Meera completes the visit, and Asha sees it.
import { test, expect, login } from "./fixtures";

test("the doctor completes a booked visit", async ({ page, browser }) => {
  await login(page, "asha");
  await page.goto("/doctors/1");
  await page.getByRole("combobox", { name: "Slot" }).click();
  await page.getByRole("option", { name: "2026-12-01 at 10:30" }).click();
  await page
    .getByRole("textbox", { name: "Reason for the visit" })
    .fill("Cough");
  await page.getByRole("button", { name: "Book" }).click();
  await expect(page.getByRole("alert")).toContainText("Booked:");

  const doctorsBrowser = await browser.newContext();
  const doctor = await doctorsBrowser.newPage();
  await login(doctor, "drmeera");
  await doctor.getByRole("link", { name: "My schedule" }).click();
  const visit = doctor.getByRole("row").filter({ hasText: "Cough" });
  await expect(visit).toContainText("Asha Verma");
  await visit.getByRole("button", { name: "Complete" }).click();
  await expect(visit).toContainText("completed");
  await doctorsBrowser.close();

  await page.getByRole("link", { name: "My appointments" }).click();
  const mine = page.getByRole("row").filter({ hasText: "Cough" });
  await expect(mine).toContainText("completed");
  await expect(mine.getByRole("button", { name: "Cancel" })).toHaveCount(0);
});
