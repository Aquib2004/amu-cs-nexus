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
      <h1>Notices</h1>
      {error ? (
        <p className="error">Could not load notices: {error}</p>
      ) : loading ? (
        <p>Loading notices&hellip;</p>
      ) : notices.length === 0 ? (
        <p>No notices yet.</p>
      ) : (
        <ul className="notice-list">
          {notices.map((n) => (
            <li key={n.id} className="notice-item">
              <a href={n.url} target="_blank" rel="noreferrer">
                {n.title}
              </a>
              <span className="notice-meta">
                {n.category ?? "general"} &middot; {n.published_at ?? "unknown date"}
              </span>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}