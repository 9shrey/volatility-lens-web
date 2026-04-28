import { test, expect } from "@playwright/test";

test("home renders shell", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /volatility & regime lens/i })).toBeVisible();
  await expect(page.getByTestId("provenance-badge")).toBeVisible();
});

test("methodology page renders", async ({ page }) => {
  await page.goto("/methodology");
  await expect(page.getByRole("heading", { level: 1, name: /methodology/i })).toBeVisible();
});
