"use client";

import { useEffect, useState } from "react";

import { getDocuments } from "@/services/documents";
import type { DocumentListItem } from "@/types/directory";

export default function DocumentsPage() {
  const [docs, setDocs] = useState<DocumentListItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDocuments({ limit: 50 })
      .then(setDocs)
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Unknown error")
      )
      .finally(() => setLoading(false));
  }, []);

  return (
    <main>
      <h1>Documents</h1>
      <p className="chat-hint">
        Indexed documents and downloads. Source data is seeded locally for
        development.
      </p>
      {error ? (
        <p className="error">Could not load documents: {error}</p>
      ) : loading ? (
        <p>Loading documents…</p>
      ) : docs.length === 0 ? (
        <p>No documents indexed yet.</p>
      ) : (
        <ul className="notice-list">
          {docs.map((d) => (
            <li key={d.id} className="notice-item">
              <strong>{d.title}</strong>
              <span className="notice-meta">
                {d.document_type ?? "document"} · {d.status}
              </span>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}