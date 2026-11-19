// Session 13: the refresh cookie in a real browser. A reload
// keeps Asha signed in; after Log out a reload does not; an expired access
// token is renewed in the middle of a booking.
import { test, expect, login } from "./fixtures";

test("a reload keeps the patient signed in", async ({ page }) => {
  await login(page, "asha");
  await page.reload(); // the access token was in memory only: it is gone
  await expect(page.getByText("asha (patient)")).toBeVisible();
});

test("after Log out, a reload stays signed out", async ({ page }) => {
  await login(page, "asha");
  await page.getByRole("button", { name: "Log out" }).click();
  await expect(page.getByRole("link", { name: "Log in" })).toBeVisible();
  await page.reload();
  await expect(page.getByRole("link", { name: "Log in" })).toBeVisible();
  await expect(page.getByText("asha (patient)")).toHaveCount(0);
});

test("an expired token is renewed during a booking", async ({ page }) => {
  const seconds = Number(process.env.JWT_ACCESS_SECONDS ?? "300");
  test.skip(seconds > 5, "run with JWT_ACCESS_SECONDS=3 (Lab Reference)");
  await login(page, "asha");
  await page.goto("/doctors/1");
  await page.getByRole("combobox", { name: "Slot" }).click();
  await page.getByRole("option", { name: "2026-12-01 at 10:30" }).click();
  // the only fixed wait of the course: the token's real life on the server
  await page.waitForTimeout((seconds + 1) * 1000);

  const answers: string[] = []; // what the API answered, in order
  page.on("response", (r) => {
    const path = new URL(r.url()).pathname;
    if (r.request().method() === "POST") answers.push(`${r.status()} ${path}`);
  });
  await page.getByRole("button", { name: "Book" }).click();
  await expect(page.getByRole("alert")).toContainText("Booked:");
  expect(answers).toEqual([
    "401 /api/v1/appointments/",
    "200 /api/v1/auth/cookie/refresh/",
    "201 /api/v1/appointments/",
  ]);
});
