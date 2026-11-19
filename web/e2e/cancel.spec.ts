// DIY: Asha cancels her appointment, and the API keeps it cancelled.
import { test, expect, login } from "./fixtures";

test("a cancel is kept by the API", async ({ page }) => {
  await login(page, "asha");
  await page.getByRole("link", { name: "My appointments" }).click();
  const row = page.getByRole("row").filter({ hasText: "Fever for two days" });
  await expect(row).toContainText("booked");
  await row.getByRole("button", { name: "Cancel" }).click();
  await expect(row).toContainText("cancelled");
  await expect(row.getByRole("button", { name: "Cancel" })).toHaveCount(0);
  await page.reload(); // a new page asks the API again
  await expect(row).toContainText("cancelled");
});
