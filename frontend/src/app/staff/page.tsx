"use client";

import { useEffect, useState } from "react";

import { getStaff } from "@/services/staff";
import type { StaffRead } from "@/types/directory";

export default function StaffPage() {
  const [items, setItems] = useState<StaffRead[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getStaff(50)
      .then(setItems)
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Unknown error")
      )
      .finally(() => setLoading(false));
  }, []);

  return (
    <main>
      <h1 className="page-title">Non-Teaching Staff</h1>
      <p className="page-subtitle">
        Administrative and technical staff of the Department of Computer
        Science, from the official AMU site.
      </p>
      {error ? (
        <p className="error">Could not load staff: {error}</p>
      ) : loading ? (
        <p className="loading">Loading staff&hellip;</p>
      ) : items.length === 0 ? (
        <div className="empty-state">No staff indexed yet.</div>
      ) : (
        <ul className="item-list">
          {items.map((s) => (
            <li key={s.id} className="item-card">
              <h2 className="item-title">{s.name}</h2>
              <div className="item-tags">
                {s.designation && <span className="badge">{s.designation}</span>}
              </div>
              {s.email && (
                <p className="item-meta">
                  <a href={`mailto:${s.email}`}>{s.email}</a>
                </p>
              )}
              {s.phone && <p className="item-meta">{s.phone}</p>}
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}