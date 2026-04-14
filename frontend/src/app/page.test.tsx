import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import Home from "@/app/page";

describe("Home sign in flow", () => {
  beforeEach(() => {
    vi.spyOn(global, "fetch").mockImplementation(async (input, init) => {
      const url = String(input);
      if (url.includes("/api/board/user") && (!init || init.method === "GET")) {
        return {
          ok: true,
          json: async () => ({
            columns: [
              { id: "col-backlog", title: "Backlog", cardIds: [] },
              { id: "col-discovery", title: "Discovery", cardIds: [] },
              { id: "col-progress", title: "In Progress", cardIds: [] },
              { id: "col-review", title: "Review", cardIds: [] },
              { id: "col-done", title: "Done", cardIds: [] },
            ],
            cards: {},
          }),
        } as Response;
      }
      if (url.includes("/api/ai/chat/user")) {
        return {
          ok: true,
          json: async () => ({
            assistant_message: "Done. I added one card.",
            board_updated: true,
            board: {
              columns: [
                {
                  id: "col-backlog",
                  title: "Backlog",
                  cardIds: ["card-1"],
                },
                { id: "col-discovery", title: "Discovery", cardIds: [] },
                { id: "col-progress", title: "In Progress", cardIds: [] },
                { id: "col-review", title: "Review", cardIds: [] },
                { id: "col-done", title: "Done", cardIds: [] },
              ],
              cards: {
                "card-1": {
                  id: "card-1",
                  title: "AI task",
                  details: "Created by assistant",
                },
              },
            },
          }),
        } as Response;
      }
      return { ok: true, json: async () => ({}) } as Response;
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("shows login form before board", () => {
    render(<Home />);
    expect(screen.getByRole("heading", { name: "Sign in" })).toBeInTheDocument();
    expect(
      screen.queryByRole("heading", { name: "Kanban Studio" })
    ).not.toBeInTheDocument();
  });

  it("shows error for wrong credentials", async () => {
    render(<Home />);
    await userEvent.type(screen.getByLabelText("Username"), "wrong");
    await userEvent.type(screen.getByLabelText("Password"), "wrong");
    await userEvent.click(screen.getByRole("button", { name: "Sign in" }));
    expect(
      screen.getByText("Invalid credentials. Use user / password.")
    ).toBeInTheDocument();
  });

  it("signs in and logs out", async () => {
    render(<Home />);
    await userEvent.type(screen.getByLabelText("Username"), "user");
    await userEvent.type(screen.getByLabelText("Password"), "password");
    await userEvent.click(screen.getByRole("button", { name: "Sign in" }));

    expect(await screen.findByRole("heading", { name: "Kanban Studio" })).toBeInTheDocument();

    await userEvent.click(screen.getByRole("button", { name: "Log out" }));
    expect(screen.getByRole("heading", { name: "Sign in" })).toBeInTheDocument();
  });

  it("sends chat and renders assistant response", async () => {
    render(<Home />);
    await userEvent.type(screen.getByLabelText("Username"), "user");
    await userEvent.type(screen.getByLabelText("Password"), "password");
    await userEvent.click(screen.getByRole("button", { name: "Sign in" }));
    await screen.findByRole("heading", { name: "Kanban Studio" });

    await userEvent.type(
      screen.getByPlaceholderText("Ask AI to create or move cards..."),
      "Add one task in backlog"
    );
    await userEvent.click(screen.getByRole("button", { name: "Send" }));

    expect(await screen.findByText("Done. I added one card.")).toBeInTheDocument();
    expect(await screen.findByText("AI task")).toBeInTheDocument();
  });
});
