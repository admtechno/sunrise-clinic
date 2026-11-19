// Sessions 12 and 13: what every browser test shares. Before each test the
// database m9_e2e is emptied and filled again (reset_test_data), so every test
// starts from the same sample data. login() signs in through the login page;
// signIn() fills the login form of the page that is open (Session 13).
import { execFileSync } from "node:child_process";
import { test as base, expect, type Page } from "@playwright/test";
import { API_DIR } from "../playwright.config";

export const test = base.extend<{ freshData: void }>({
  freshData: [
    async ({}, use) => {
      execFileSync("python", ["manage.py", "reset_test_data"], {
        cwd: API_DIR,
        env: { ...process.env, DJANGO_SETTINGS_MODULE: "config.settings.e2e" },
        stdio: "pipe", // its one line is not needed in the report
      });
      await use();
    },
    // auto: for every test, without asking. The reset has its own time limit, so
    // a slow start of Python (about 7 s on some Windows PCs) does not use up the
    // test's own 30 s (or the 10 s of a test that sets a shorter limit).
    { auto: true, timeout: 60_000 },
  ],
});
export { expect };

export async function login(page: Page, username: string) {
  await page.goto("/login");
  await signIn(page, username);
}

export async function signIn(page: Page, username: string) {
  const password = process.env.E2E_PASSWORD; // never written in a test file
  if (!password) throw new Error("Set E2E_PASSWORD first (Lab Reference).");
  await page.getByRole("textbox", { name: "Username" }).fill(username);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Log in" }).click();
  // signed in when the menu shows the name
  await expect(page.getByText(`${username} (`)).toBeVisible();
}
