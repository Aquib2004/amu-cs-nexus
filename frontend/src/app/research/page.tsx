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
      <h1>Research</h1>
      <p className="chat-hint">
        Research and publications associated with the department.
      </p>
      {error ? (
        <p className="error">Could not load research: {error}</p>
      ) : loading ? (
        <p>Loading research…</p>
      ) : items.length === 0 ? (
        <p>No research records indexed yet.</p>
      ) : (
        <ul className="notice-list">
          {items.map((d) => (
            <li key={d.id} className="notice-item">
              <strong>{d.title}</strong>
              <span className="notice-meta">{d.document_type}</span>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}