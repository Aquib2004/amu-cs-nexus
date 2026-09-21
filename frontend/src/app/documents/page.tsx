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
      <h1 className="page-title">Documents</h1>
      <p className="page-subtitle">
        Indexed documents with links to the official source pages.
      </p>
      {error ? (
        <p className="error">Could not load documents: {error}</p>
      ) : loading ? (
        <p className="loading">Loading documents&hellip;</p>
      ) : docs.length === 0 ? (
        <div className="empty-state">No documents indexed yet.</div>
      ) : (
        <ul className="item-list">
          {docs.map((d) => (
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
                <span className="badge">{d.document_type ?? "document"}</span>
                <span className="badge warm">{d.status}</span>
              </div>
              <span className="item-meta">
                {d.source_type ?? "source"} · {d.department ?? "computer-science"}
              </span>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}