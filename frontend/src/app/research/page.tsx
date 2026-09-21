"use client";

import { useEffect, useState } from "react";

import { getResearch } from "@/services/research";
import type { DocumentListItem } from "@/types/directory";

export default function ResearchPage() {
  const [items, setItems] = useState<DocumentListItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getResearch(20)
      .then(setItems)
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Unknown error")
      )
      .finally(() => setLoading(false));
  }, []);

  return (
    <main>
      <h1 className="page-title">Research</h1>
      <p className="page-subtitle">
        Research and publications associated with the department.
      </p>
      {error ? (
        <p className="error">Could not load research: {error}</p>
      ) : loading ? (
        <p className="loading">Loading research&hellip;</p>
      ) : items.length === 0 ? (
        <div className="empty-state">No research records indexed yet.</div>
      ) : (
        <ul className="item-list">
          {items.map((d) => (
            <li key={d.id} className="item-card">
              <h2 className="item-title">
                {d.source_url ? (
                  <a href={d.source_url} target="_blank" rel="noreferrer">
                    {d.title}
                  </a>
                ) : (
                  d.title
                )}
              </h2>
              <div className="item-tags">
                <span className="badge">{d.document_type ?? "publication"}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}