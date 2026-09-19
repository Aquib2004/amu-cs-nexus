"use client";

import { useState } from "react";

import { askQuestion } from "@/services/chat";
import type { ChatResponse } from "@/types";

export default function ChatPage() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    const q = question.trim();
    if (!q || loading) return;
    setError(null);
    setLoading(true);
    try {
      setResult(await askQuestion(q));
    } catch (err: unknown) {
      setResult(null);
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>Chat</h1>
      <p className="chat-hint">
        Ask about indexed official AMU Computer Science information (notices,
        facilities, documents). Answers are grounded in retrieved sources.
      </p>
      <form onSubmit={onSubmit}>
        <label htmlFor="question">Ask a question</label>
        <input
          id="question"
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. When was the MCA admission notice published?"
        />
        <button type="submit" disabled={loading}>
          {loading ? "Thinking…" : "Ask"}
        </button>
      </form>

      {error ? (
        <p className="error">
          Could not reach the backend: {error}. Start it with `uvicorn
          app.main:app` in the backend folder.
        </p>
      ) : result ? (
        <div className="chat-answer">
          <p>{result.answer}</p>
          {result.sources.length > 0 && (
            <ul className="source-list">
              {result.sources.map((s) => (
                <li key={s.number} className="source-item">
                  <span>[{s.number}]</span>
                  <a href={s.source_url} target="_blank" rel="noreferrer">
                    {s.source_url}
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      ) : (
        <p>Ask a question above to see a source-grounded answer.</p>
      )}
    </main>
  );
}