"use client";

import { useEffect, useState } from "react";

import { getNotices } from "@/services/notices";
import type { Notice } from "@/types";

export default function NoticesPage() {
  const [notices, setNotices] = useState<Notice[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getNotices({ limit: 50 })
      .then(setNotices)
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Unknown error")
      )
      .finally(() => setLoading(false));
  }, []);

  return (
    <main>
      <h1 className="page-title">Notices</h1>
      <p className="page-subtitle">
        Department notices and announcements (development sample data).
      </p>
      {error ? (
        <p className="error">Could not load notices: {error}</p>
      ) : loading ? (
        <p className="loading">Loading notices&hellip;</p>
      ) : notices.length === 0 ? (
        <div className="empty-state">No notices yet.</div>
      ) : (
        <ul className="item-list">
          {notices.map((n) => (
            <li key={n.id} className="item-card">
              <h2 className="item-title">
                <a href={n.url} target="_blank" rel="noreferrer">
                  {n.title}
                </a>
              </h2>
              <div className="item-tags">
                <span className="badge">{n.category ?? "general"}</span>
                <span className="badge warm">{n.published_at ?? "date unknown"}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}