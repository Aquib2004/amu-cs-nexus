"use client";

import { useEffect, useState } from "react";

import { getHealth } from "@/services/health";
import type { HealthResponse } from "@/types";

const FEATURES: { title: string; href: string; blurb: string }[] = [
  {
    title: "YouRobo",
    href: "/chat",
    blurb: "Ask questions about the department; answers come with numbered sources.",
  },
  {
    title: "Search",
    href: "/search",
    blurb: "Keyword and semantic search across notices, documents and pages.",
  },
  {
    title: "Notices",
    href: "/notices",
    blurb: "Department notices and announcements.",
  },
  {
    title: "Documents",
    href: "/documents",
    blurb: "Indexed documents with links to the official source pages.",
  },
  {
    title: "Faculty",
    href: "/faculty",
    blurb: "Faculty directory for the Department of Computer Science.",
  },
  {
    title: "Research",
    href: "/research",
    blurb: "Research publications and project areas.",
  },
  {
    title: "Exams",
    href: "/exams",
    blurb: "Official Controller of Examinations portals and NEP cell.",
  },
];

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Unknown error")
      );
  }, []);

  return (
    <main>
      <section className="hero">
        <h1>AMUCS Nexus</h1>
        <p>
          Knowledge, search, and a source-grounded AI assistant for the AMU
          Department of Computer Science. Ask YouRobo, search the indexed
          content, or browse notices, documents, faculty and research directly.
        </p>
        <div className="field-row">
          <a className="btn" href="/chat">
            Ask YouRobo
          </a>
          <a className="btn secondary" href="/search">
            Search content
          </a>
        </div>
      </section>

      <section className="card-grid">
        {FEATURES.map((f) => (
          <a key={f.title} className="feature-card" href={f.href}>
            <span className="feature-title">{f.title}</span>
            <p>{f.blurb}</p>
          </a>
        ))}
      </section>

      <section className="card" style={{ marginTop: "1.6rem" }}>
        <h2>Backend status</h2>
        {error ? (
          <p className="error">
            Could not reach the backend: {error}. Start it with `uvicorn
            app.main:app` in the backend folder.
          </p>
        ) : health ? (
          <dl className="status-grid">
            <div>
              <dt>Status</dt>
              <dd>{health.status}</dd>
            </div>
            <div>
              <dt>Application</dt>
              <dd>{health.application}</dd>
            </div>
            <div>
              <dt>Version</dt>
              <dd>{health.version}</dd>
            </div>
            <div>
              <dt>Environment</dt>
              <dd>{health.environment}</dd>
            </div>
          </dl>
        ) : (
          <p className="loading">Checking backend&hellip;</p>
        )}
      </section>
    </main>
  );
}