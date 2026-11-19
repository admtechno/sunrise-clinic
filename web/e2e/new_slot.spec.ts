// DIY: reception adds a slot, and a patient books it, in two browsers.
import { test, expect, login } from "./fixtures";

test("a slot added by reception can be booked", async ({ page, browser }) => {
  await login(page, "reception");
  await page.getByRole("link", { name: "Slots" }).click();
  await page.getByRole("textbox", { name: "Date" }).fill("2026-12-03");
  await page.getByRole("textbox", { name: "Time" }).fill("09:30");
  await page.getByRole("button", { name: "Add slot" }).click();
  const row = page.getByRole("row").filter({ hasText: "2026-12-03" });
  await expect(row).toContainText("09:30");
  await expect(row).toContainText("no"); // not booked yet

  const ashasBrowser = await browser.newContext();
  const asha = await ashasBrowser.newPage();
  await login(asha, "asha");
  await asha.goto("/doctors/1");
  await expect(asha.getByText("2026-12-03 at 09:30")).toBeVisible();
  await asha.getByRole("combobox", { name: "Slot" }).click();
  await asha.getByRole("option", { name: "2026-12-03 at 09:30" }).click();
  await asha.getByRole("button", { name: "Book" }).click();
  await expect(asha.getByRole("alert")).toContainText("Booked: 2026-12-03");
  await ashasBrowser.close();

  await page.reload(); // reception sees the slot as booked now
  await expect(row).toContainText("yes");
});
