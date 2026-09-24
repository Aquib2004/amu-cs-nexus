"use client";

import { useEffect, useState } from "react";

import { getPrograms } from "@/services/programs";
import type { ProgramRead } from "@/types/directory";

const LEVEL_LABEL: Record<string, string> = {
  ug: "Undergraduate",
  pg: "Postgraduate",
  phd: "Doctoral (PhD)",
};

export default function ProgramsPage() {
  const [items, setItems] = useState<ProgramRead[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getPrograms(50)
      .then(setItems)
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Unknown error")
      )
      .finally(() => setLoading(false));
  }, []);

  return (
    <main>
      <h1 className="page-title">Programmes</h1>
      <p className="page-subtitle">
        Degrees offered by the Department of Computer Science, loaded from the
        official AMU site.
      </p>
      {error ? (
        <p className="error">Could not load programmes: {error}</p>
      ) : loading ? (
        <p className="loading">Loading programmes&hellip;</p>
      ) : items.length === 0 ? (
        <div className="empty-state">No programmes indexed yet.</div>
      ) : (
        <ul className="item-list">
          {items.map((p) => (
            <li key={p.id} className="item-card">
              <h2 className="item-title">{p.name}</h2>
              <div className="item-tags">
                <span className="badge">
                  {LEVEL_LABEL[p.level ?? ""] ?? (p.level ?? "programme")}
                </span>
                {p.intake_seats && (
                  <span className="badge">Intake: {p.intake_seats}</span>
                )}
              </div>
              {p.eligibility && (
                <p className="item-meta">
                  <strong>Eligibility/specialisation:</strong> {p.eligibility}
                </p>
              )}
              {p.details && (
                <p className="item-meta">
                  <strong>Details:</strong> {p.details.length > 240
                    ? `${p.details.slice(0, 240)}…`
                    : p.details}
                </p>
              )}
              <a href={p.source_url} target="_blank" rel="noreferrer">
                Official page
              </a>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}