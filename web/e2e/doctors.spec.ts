// Session 12: the doctors list in a real browser, on
// the real API. Nobody is signed in.
import { test, expect } from "./fixtures";

test("the first page lists three doctors", async ({ page }) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Sunrise Clinic Desk" }),
  ).toBeVisible();
  await expect(page.getByText("Page 1 of 3, 8 doctors")).toBeVisible();
  await expect(page.getByRole("row")).toHaveCount(4); // the head and 3 doctors
});

test("a speciality filter changes the address", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Paediatrics" }).click();
  await expect(page).toHaveURL(/\?speciality=paediatrics$/);
  // the new list, not the old one that is still shown while it loads
  await expect(page.getByText("Page 1 of 1, 3 doctors")).toBeVisible();
  const rows = page.getByRole("row").filter({ hasText: "Paediatrics" });
  await expect(rows).toHaveCount(3);
  await expect(
    page.getByRole("row").filter({ hasText: "General Medicine" }),
  ).toHaveCount(0);
});

test("a search, then a click opens the doctor", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("textbox", { name: "Search name" }).fill("Meera");
  await page.getByRole("button", { name: "Search" }).click();
  await expect(page).toHaveURL(/\?search=Meera$/);
  await page.getByRole("cell", { name: "Dr. Meera Shah" }).click();
  await expect(page).toHaveURL("/doctors/1");
  await expect(
    page.getByRole("heading", { name: "Dr. Meera Shah" }),
  ).toBeVisible();
  await expect(page.getByText("2026-12-01 at 10:30")).toBeVisible();
  await expect(page.getByText("Log in as a patient to book.")).toBeVisible();
});
