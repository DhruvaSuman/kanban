import { expect, test, type Page } from "@playwright/test";

const login = async (page: Page) => {
  await page.getByLabel("Username").fill("user");
  await page.getByLabel("Password").fill("password");
  await page.getByRole("button", { name: "Sign in" }).click();
};

test("loads the kanban board", async ({ page }) => {
  await page.goto("/");
  await login(page);
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
});

test("adds a card to a column", async ({ page }) => {
  await page.goto("/");
  await login(page);
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill("Playwright card");
  await firstColumn.getByPlaceholder("Details").fill("Added via e2e.");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText("Playwright card")).toBeVisible();
});

test("moves a card between columns", async ({ page }) => {
  await page.goto("/");
  await login(page);
  const card = page.getByTestId("card-card-1");
  const targetColumn = page.getByTestId("column-col-review");
  const cardBox = await card.boundingBox();
  const columnBox = await targetColumn.boundingBox();
  if (!cardBox || !columnBox) {
    throw new Error("Unable to resolve drag coordinates.");
  }

  await page.mouse.move(
    cardBox.x + cardBox.width / 2,
    cardBox.y + cardBox.height / 2
  );
  await page.mouse.down();
  await page.mouse.move(
    columnBox.x + columnBox.width / 2,
    columnBox.y + 120,
    { steps: 12 }
  );
  await page.mouse.up();
  await expect(targetColumn.getByTestId("card-card-1")).toBeVisible();
});

test("rejects invalid credentials and supports logout", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Username").fill("invalid");
  await page.getByLabel("Password").fill("invalid");
  await page.getByRole("button", { name: "Sign in" }).click();
  await expect(
    page.getByText("Invalid credentials. Use user / password.")
  ).toBeVisible();

  await login(page);
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  await page.getByRole("button", { name: "Log out" }).click();
  await expect(page.getByRole("heading", { name: "Sign in" })).toBeVisible();
});

test("persists board changes after refresh", async ({ page }) => {
  await page.goto("/");
  await login(page);

  const firstColumn = page.locator('[data-testid="column-col-backlog"]');
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill("Persistent card");
  await firstColumn.getByPlaceholder("Details").fill("Should survive refresh.");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText("Persistent card")).toBeVisible();

  await page.reload();
  await login(page);
  await expect(firstColumn.getByText("Persistent card")).toBeVisible();
});

test("renders AI chat response and applies board update", async ({ page }) => {
  await page.route("**/api/ai/chat/user", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        assistant_message: "Added AI-generated task.",
        board_updated: true,
        board: {
          columns: [
            { id: "col-backlog", title: "Backlog", cardIds: ["card-ai"] },
            { id: "col-discovery", title: "Discovery", cardIds: [] },
            { id: "col-progress", title: "In Progress", cardIds: [] },
            { id: "col-review", title: "Review", cardIds: [] },
            { id: "col-done", title: "Done", cardIds: [] },
          ],
          cards: {
            "card-ai": {
              id: "card-ai",
              title: "AI generated task",
              details: "Created from chat",
            },
          },
        },
      }),
    });
  });

  await page.goto("/");
  await login(page);
  await page
    .getByPlaceholder("Ask AI to create or move cards...")
    .fill("Add a task in backlog");
  await page.getByRole("button", { name: "Send" }).click();

  await expect(page.getByText("Added AI-generated task.")).toBeVisible();
  await expect(page.getByText("AI generated task")).toBeVisible();
});
