// Session 13: what each role finds, and what it is refused.
import { test, expect, login, signIn } from "./fixtures";

const homes = [
  { username: "asha", link: "My appointments", heading: "My appointments" },
  { username: "drmeera", link: "My schedule", heading: "My schedule" },
  { username: "reception", link: "Slots", heading: "Slots" },
];

for (const { username, link, heading } of homes) {
  test(`${username} finds ${link} in the menu`, async ({ page }) => {
    await login(page, username);
    await page.getByRole("link", { name: link }).click();
    await expect(page.getByRole("heading", { name: heading })).toBeVisible();
  });
}

test("a patient is turned away from the schedule", async ({ page }) => {
  await login(page, "asha");
  await page.goto("/schedule"); // typed into the address bar
  await expect(page.getByRole("alert")).toHaveText(
    "This page is for doctor logins. You are logged in as asha.",
  );
  await expect(page.getByRole("link", { name: "My schedule" })).toHaveCount(0);
});

test("a visitor logs in and lands where they wanted", async ({ page }) => {
  await page.goto("/appointments");
  await expect(page).toHaveURL("/login");
  await signIn(page, "asha");
  await expect(page).toHaveURL("/appointments");
  await expect(
    page.getByRole("heading", { name: "My appointments" }),
  ).toBeVisible();
});
