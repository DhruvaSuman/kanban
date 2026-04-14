"use client";

import { FormEvent, useEffect, useState } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";
import { initialData, type BoardData } from "@/lib/kanban";

const USERNAME = "user";
const PASSWORD = "password";
const LOCAL_BOARD_KEY = "pm-board-user";
type ChatRole = "user" | "assistant";

type ChatMessage = {
  role: ChatRole;
  content: string;
};

export default function Home() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isSignedIn, setIsSignedIn] = useState(false);
  const [error, setError] = useState("");
  const [board, setBoard] = useState<BoardData>(initialData);
  const [isLoadingBoard, setIsLoadingBoard] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [isSendingChat, setIsSendingChat] = useState(false);
  const [chatError, setChatError] = useState("");

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

  const handleSendChat = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const question = chatInput.trim();
    if (!question || isSendingChat) {
      return;
    }
    setIsSendingChat(true);
    setChatError("");
    const nextMessages = [...chatMessages, { role: "user" as const, content: question }];
    setChatMessages(nextMessages);
    setChatInput("");

    try {
      const response = await fetch("/api/ai/chat/user", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          conversation_history: chatMessages.map((message) => ({
            role: message.role,
            content: message.content,
          })),
        }),
      });
      if (!response.ok) {
        throw new Error("Unable to get AI response.");
      }
      const payload = (await response.json()) as {
        assistant_message: string;
        board: BoardData;
        board_updated: boolean;
      };
      setChatMessages((previous) => [
        ...previous,
        { role: "assistant", content: payload.assistant_message },
      ]);
      if (payload.board_updated) {
        setBoard(payload.board);
        window.localStorage.setItem(LOCAL_BOARD_KEY, JSON.stringify(payload.board));
      }
    } catch {
      setChatMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: "I could not reach AI right now. Please try again.",
        },
      ]);
      setChatError("Chat request failed.");
    } finally {
      setIsSendingChat(false);
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
      <div className="pr-[370px]">
        {isLoadingBoard ? (
          <main className="mx-auto flex min-h-screen w-full max-w-md items-center justify-center px-6">
            <p className="text-sm font-semibold text-[var(--gray-text)]">
              Loading board...
            </p>
          </main>
        ) : (
          <KanbanBoard board={board} onBoardChange={persistBoard} />
        )}
      </div>
      <aside className="fixed right-0 top-0 z-40 flex h-screen w-[350px] flex-col border-l border-[var(--stroke)] bg-white/95 p-4 shadow-[-10px_0_24px_rgba(3,33,71,0.08)] backdrop-blur">
        <div className="mb-3 border-b border-[var(--stroke)] pb-3">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]">
            AI Assistant
          </p>
          <h2 className="mt-2 font-display text-xl font-semibold text-[var(--navy-dark)]">
            Board Chat
          </h2>
          <p className="mt-1 text-xs text-[var(--gray-text)]">
            Ask for card edits, moves, and planning help.
          </p>
        </div>

        <div className="flex-1 space-y-3 overflow-y-auto pr-1" data-testid="chat-messages">
          {chatMessages.length === 0 ? (
            <p className="rounded-xl border border-dashed border-[var(--stroke)] p-3 text-xs text-[var(--gray-text)]">
              No messages yet. Ask AI to update your board.
            </p>
          ) : (
            chatMessages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={
                  message.role === "user"
                    ? "ml-8 rounded-2xl bg-[var(--secondary-purple)] px-3 py-2 text-sm text-white"
                    : "mr-6 rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] px-3 py-2 text-sm text-[var(--navy-dark)]"
                }
              >
                {message.content}
              </div>
            ))
          )}
        </div>

        <form className="mt-3 space-y-2" onSubmit={handleSendChat}>
          <label className="block text-xs font-semibold uppercase tracking-[0.16em] text-[var(--gray-text)]">
            Message
            <textarea
              className="mt-2 h-24 w-full resize-none rounded-xl border border-[var(--stroke)] px-3 py-2 text-sm outline-none focus:border-[var(--primary-blue)]"
              value={chatInput}
              onChange={(event) => setChatInput(event.target.value)}
              placeholder="Ask AI to create or move cards..."
            />
          </label>
          {chatError ? (
            <p className="text-xs font-semibold text-[var(--secondary-purple)]">{chatError}</p>
          ) : null}
          <button
            type="submit"
            disabled={isSendingChat}
            className="w-full rounded-xl bg-[var(--secondary-purple)] px-4 py-2 text-sm font-semibold text-white disabled:opacity-70"
          >
            {isSendingChat ? "Sending..." : "Send"}
          </button>
        </form>
      </aside>
    </>
  );
}
