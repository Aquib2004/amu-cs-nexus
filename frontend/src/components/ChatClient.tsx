"use client";

import { useRef, useState } from "react";
import { askQuestion, deleteChatFile, uploadChatFile } from "@/services/chat";
import type { ChatResponse, ChatUpload } from "@/types";

const SUGGESTIONS = [
  "Who is Arman Rasool Faridi?",
  "Show the latest department notices",
  "Which laboratories and research projects are available?",
  "How do I check an official examination result?",
];

type Turn = { role: "user" | "bot"; text: string; response?: ChatResponse };

export default function ChatClient() {
  const [question, setQuestion] = useState("");
  const [turns, setTurns] = useState<Turn[]>([]);
  const [upload, setUpload] = useState<ChatUpload | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);

  async function ask(value: string) {
    const text = value.trim();
    if (!text || loading) return;
    setError(null);
    setQuestion("");
    setTurns((current) => [...current, { role: "user", text }]);
    setLoading(true);
    try {
      const result = await askQuestion(text, upload);
      setTurns((current) => [...current, { role: "bot", text: result.answer, response: result }]);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  async function selectFile(file: File | undefined) {
    if (!file) return;
    setError(null);
    setUploading(true);
    try {
      const replacement = await uploadChatFile(file);
      if (upload) await deleteChatFile(upload);
      setUpload(replacement);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      if (fileInput.current) fileInput.current.value = "";
    }
  }

  async function clearFile() {
    if (!upload) return;
    const previous = upload;
    setUpload(null);
    try {
      await deleteChatFile(previous);
    } catch (err: unknown) {
      setUpload(previous);
      setError(err instanceof Error ? err.message : "Could not remove file");
    }
  }

  const latest = [...turns].reverse().find((turn) => turn.response)?.response;
  const provider = upload ? "Private file" : latest?.provider === "gemini" ? "Gemini" : latest?.provider === "groq" ? "Groq (120B)" : "Grounded";

  return (
    <main>
      <section className="chat-panel">
        <header className="chat-head">
          <div className="chat-identity"><img src="/amu-logo.png" alt="" width={30} height={30} />YouRobo <span className="badge">{provider}</span></div>
          <p className="chat-status">Official AMU answers and private student-file Q&amp;A, with citations.</p>
        </header>

        <div className="chat-scope" aria-live="polite">
          {upload ? (
            <div className="file-chip"><span><strong>{upload.filename}</strong> · {upload.chunk_count} sections · expires in 24h</span><button type="button" className="link-button" onClick={() => void clearFile()}>Remove</button></div>
          ) : <span>Verified sources: notices, faculty, programmes, labs, research, staff, documents and exams.</span>}
          <label className="btn secondary file-picker">{uploading ? "Reading file…" : upload ? "Replace file" : "Add notes or paper"}<input ref={fileInput} type="file" accept=".pdf,.docx,.txt,.md,.markdown" disabled={uploading || loading} onChange={(event) => void selectFile(event.target.files?.[0])} /></label>
        </div>

        <div className="chat-thread" aria-live="polite">
          {turns.length === 0 && <div className="chat-welcome"><strong>What would you like to know?</strong><span>Answers cite their evidence and never invent missing details.</span></div>}
          {turns.map((turn, index) => (
            <div key={index} className={`msg ${turn.role}`}>
              <div>{turn.text}</div>
              {turn.response?.notice && <div className="inline-notice">{turn.response.notice}</div>}
              {!!turn.response?.sources.length && <details className="sources-panel"><summary>Sources ({turn.response.sources.length})</summary><ol>{turn.response.sources.map((source) => <li key={`${index}-${source.number}-${source.chunk_id}`}><strong>{source.title}</strong> {source.source_type === "upload" ? <span className="badge">Private file</span> : <a href={source.source_url} target="_blank" rel="noreferrer">Open source</a>}</li>)}</ol></details>}
            </div>
          ))}
          {loading && <div className="msg-typing">YouRobo is thinking…</div>}
        </div>

        <form className="chat-composer field-row" onSubmit={(event) => { event.preventDefault(); void ask(question); }}>
          <label htmlFor="question">Your question</label><input id="question" type="text" value={question} maxLength={500} onChange={(event) => setQuestion(event.target.value)} placeholder={upload ? `Ask about ${upload.filename}…` : "Ask about notices, faculty, exams, research…"} /><button type="submit" className="btn" disabled={loading || uploading}>Ask</button>
        </form>
        {turns.length === 0 && <div className="suggestions" role="group" aria-label="Suggested questions">{SUGGESTIONS.map((item) => <button key={item} type="button" className="suggestion-chip" onClick={() => void ask(item)}>{item}</button>)}</div>}
        {error && <p className="error">{error}</p>}
      </section>
    </main>
  );
}
