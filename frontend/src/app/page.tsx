"use client";

import { useEffect, useState } from "react";

import { getHealth } from "@/services/health";
import type { HealthResponse } from "@/types";

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
          An open-source knowledge, search, and AI information platform for the AMU
          Department of Computer Science.
        </p>
      </section>

      <section className="status-card">
        <h2>Backend status</h2>
        {error ? (
          <p className="error">
            Could not reach the backend: {error}. Start it with `uvicorn
            app.main:app` in the backend folder.
          </p>
        ) : health ? (
          <dl>
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
          <p>Checking backend&hellip;</p>
        )}
      </section>
    </main>
  );
}