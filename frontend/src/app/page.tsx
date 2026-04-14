"use client";

import { FormEvent, useEffect, useState } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";
import { initialData, type BoardData } from "@/lib/kanban";

const USERNAME = "user";
const PASSWORD = "password";
const LOCAL_BOARD_KEY = "pm-board-user";

export default function Home() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isSignedIn, setIsSignedIn] = useState(false);
  const [error, setError] = useState("");
  const [board, setBoard] = useState<BoardData>(initialData);
  const [isLoadingBoard, setIsLoadingBoard] = useState(false);

  useEffect(() => {
    if (!isSignedIn) {
      return;
    }
    let isMounted = true;
    setIsLoadingBoard(true);
    fetch("/api/board/user")
      .then(async (response) => {
        if (!response.ok) {
          throw new Error("Failed to load board");
        }
        return (await response.json()) as BoardData;
      })
      .then((payload) => {
        if (isMounted) {
          setBoard(payload);
        }
      })
      .catch(() => {
        if (isMounted) {
          const localBoardRaw = window.localStorage.getItem(LOCAL_BOARD_KEY);
          if (localBoardRaw) {
            try {
              const localBoard = JSON.parse(localBoardRaw) as BoardData;
              setBoard(localBoard);
              return;
            } catch {
              // Ignore bad local storage payload and fall back.
            }
          }
          setBoard(initialData);
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsLoadingBoard(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, [isSignedIn]);

  const persistBoard = async (nextBoard: BoardData) => {
    setBoard(nextBoard);
    window.localStorage.setItem(LOCAL_BOARD_KEY, JSON.stringify(nextBoard));
    try {
      await fetch("/api/board/user", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(nextBoard),
      });
    } catch {
      // Keep UI responsive even when local dev runs without backend.
    }
  };

  const handleLogin = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (username === USERNAME && password === PASSWORD) {
      setIsSignedIn(true);
      setError("");
      return;
    }
    setError("Invalid credentials. Use user / password.");
  };

  if (!isSignedIn) {
    return (
      <main className="mx-auto flex min-h-screen w-full max-w-md items-center px-6">
        <section className="w-full rounded-3xl border border-[var(--stroke)] bg-white p-8 shadow-[var(--shadow)]">
          <h1 className="font-display text-3xl font-semibold text-[var(--navy-dark)]">
            Sign in
          </h1>
          <p className="mt-2 text-sm text-[var(--gray-text)]">
            Use the MVP credentials to access your board.
          </p>
          <form className="mt-6 space-y-4" onSubmit={handleLogin}>
            <label className="block">
              <span className="text-sm font-semibold text-[var(--navy-dark)]">
                Username
              </span>
              <input
                className="mt-2 w-full rounded-xl border border-[var(--stroke)] px-3 py-2 outline-none focus:border-[var(--primary-blue)]"
                autoComplete="username"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
              />
            </label>
            <label className="block">
              <span className="text-sm font-semibold text-[var(--navy-dark)]">
                Password
              </span>
              <input
                className="mt-2 w-full rounded-xl border border-[var(--stroke)] px-3 py-2 outline-none focus:border-[var(--primary-blue)]"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
              />
            </label>
            {error ? (
              <p className="text-sm font-semibold text-[var(--secondary-purple)]">
                {error}
              </p>
            ) : null}
            <button
              type="submit"
              className="w-full rounded-xl bg-[var(--secondary-purple)] px-4 py-2 text-sm font-semibold text-white"
            >
              Sign in
            </button>
          </form>
        </section>
      </main>
    );
  }

  return (
    <>
      <div className="fixed right-6 top-6 z-50">
        <button
          onClick={() => {
            setIsSignedIn(false);
            setUsername("");
            setPassword("");
            setError("");
          }}
          className="rounded-full border border-[var(--stroke)] bg-white px-4 py-2 text-xs font-semibold uppercase tracking-[0.16em] text-[var(--navy-dark)] shadow-sm"
        >
          Log out
        </button>
      </div>
      {isLoadingBoard ? (
        <main className="mx-auto flex min-h-screen w-full max-w-md items-center justify-center px-6">
          <p className="text-sm font-semibold text-[var(--gray-text)]">
            Loading board...
          </p>
        </main>
      ) : (
        <KanbanBoard board={board} onBoardChange={persistBoard} />
      )}
    </>
  );
}
