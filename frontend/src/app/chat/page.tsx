"use client";

import { useState } from "react";

import { askQuestion } from "@/services/chat";
import type { ChatResponse } from "@/types";

const SUGGESTIONS = [
  "When was the MCA admission notice published?",
  "What is in the computer vision laboratory?",
  "Find a research publication",
];

interface ChatTurn {
  role: "user" | "bot";
  text: string;
}

export default function ChatPage() {
  const [question, setQuestion] = useState("");
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [sourceRefs, setSourceRefs] = useState<ChatResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function ask(q: string) {
    const text = q.trim();
    if (!text || loading) return;
    setError(null);
    setQuestion("");
    setTurns([...turns, { role: "user", text }]);
    setLoading(true);
    setSourceRefs(null);
    try {
      const result = await askQuestion(text);
      setTurns([...turns, { role: "user", text }, { role: "bot", text: result.answer }]);
      setSourceRefs(result);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Unknown error";
      setTurns([...turns, { role: "user", text }, { role: "bot", text: `Sorry, I hit an error: ${message}` }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <section className="chat-panel">
        <div className="chat-head">
          <div className="chat-identity">
            <img src="/amu-logo.png" alt="" width={30} height={30} />
            YouRobo
            <span className="badge">
              {sourceRefs?.provider === "gemini"
                ? "Gemini"
                : sourceRefs?.provider === "groq"
                  ? "Groq (70B)"
                  : "Grounded"}
            </span>
          </div>
          <p className="chat-status">
            Answers are grounded in indexed official sources and cited with
            numbers you can click.
          </p>
        </div>

        <div className="chat-thread" aria-live="polite">
          {turns.length === 0 && (
            <p className="loading">
              Ask a question below. Example: &ldquo;When was the MCA admission
              notice published?&rdquo;
            </p>
          )}
          {turns.map((t, i) => (
            <div key={i} className={t.role === "user" ? "msg user" : "msg bot"}>
              {t.text}
            </div>
          ))}
          {loading && <div className="msg-typing">YouRobo is thinking…</div>}
        </div>

        {sourceRefs?.notice && (
          <div className="notice-banner">{sourceRefs.notice}</div>
        )}

        {sourceRefs && sourceRefs.sources.length > 0 && (
          <details className="sources-panel">
            <summary>Sources ({sourceRefs.sources.length})</summary>
            <ol>
              {sourceRefs.sources.map((s) => (
                <li key={s.number}>
                  <a href={s.source_url} target="_blank" rel="noreferrer">
                    {s.source_url}
                  </a>
                </li>
              ))}
            </ol>
          </details>
        )}

        <form
          className="field-row"
          onSubmit={(e) => {
            e.preventDefault();
            ask(question);
          }}
        >
          <label htmlFor="question">Ask a question</label>
          <input
            id="question"
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. When was the MCA admission notice published?"
            aria-label="Ask YouRobo a question"
          />
          <button type="submit" className="btn" disabled={loading}>
            {loading ? "Thinking…" : "Ask"}
          </button>
        </form>

        {turns.length === 0 && (
          <div className="suggestions" role="group" aria-label="Suggested questions">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                type="button"
                className="suggestion-chip"
                onClick={() => ask(s)}
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {error && <p className="error">Could not reach the backend: {error}</p>}
      </section>
    </main>
  );
}