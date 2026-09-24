"use client";

import { useEffect, useState } from "react";

import { getLaboratories } from "@/services/laboratories";
import type { LaboratoryRead } from "@/types/directory";

export default function LaboratoriesPage() {
  const [items, setItems] = useState<LaboratoryRead[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getLaboratories(50)
      .then(setItems)
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Unknown error")
      )
      .finally(() => setLoading(false));
  }, []);

  return (
    <main>
      <h1 className="page-title">Laboratories</h1>
      <p className="page-subtitle">
        Important teaching and research laboratories of the Department of
        Computer Science, from the official AMU site.
      </p>
      {error ? (
        <p className="error">Could not load laboratories: {error}</p>
      ) : loading ? (
        <p className="loading">Loading laboratories&hellip;</p>
      ) : items.length === 0 ? (
        <div className="empty-state">No laboratories indexed yet.</div>
      ) : (
        <ul className="item-list">
          {items.map((lab) => (
            <li key={lab.id} className="item-card">
              <h2 className="item-title">{lab.name}</h2>
              {lab.description && (
                <p className="item-meta">{lab.description}</p>
              )}
              <a href={lab.source_url} target="_blank" rel="noreferrer">
                Official page
              </a>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}