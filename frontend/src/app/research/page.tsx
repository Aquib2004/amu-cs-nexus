"use client";

import { useEffect, useState } from "react";

import { getResearchProjects } from "@/services/researchProjects";
import type { ResearchProjectRead } from "@/types/directory";

const STATUS_LABEL: Record<string, string> = {
  completed: "Completed",
  ongoing: "Ongoing",
};

export default function ResearchPage() {
  const [items, setItems] = useState<ResearchProjectRead[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getResearchProjects(50)
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
        Research projects of the Department of Computer Science, loaded from
        the official AMU site.
      </p>
      {error ? (
        <p className="error">Could not load research: {error}</p>
      ) : loading ? (
        <p className="loading">Loading research&hellip;</p>
      ) : items.length === 0 ? (
        <div className="empty-state">No research projects indexed yet.</div>
      ) : (
        <ul className="item-list">
          {items.map((p) => (
            <li key={p.id} className="item-card">
              <h2 className="item-title">{p.title}</h2>
              <div className="item-tags">
                <span className="badge">
                  {STATUS_LABEL[p.status ?? ""] ?? (p.status ?? "research")}
                </span>
                {p.funding_agency && (
                  <span className="badge">Funded by: {p.funding_agency}</span>
                )}
              </div>
              {p.principal_investigator && (
                <p className="item-meta">
                  <strong>Principal investigator:</strong>{" "}
                  {p.principal_investigator}
                </p>
              )}
              {p.amount && (
                <p className="item-meta">
                  <strong>Sanctioned amount:</strong> {p.amount}
                </p>
              )}
              {p.co_investigators && (
                <p className="item-meta">
                  <strong>Co-investigators:</strong> {p.co_investigators}
                </p>
              )}
              {p.description && p.description !== p.title && (
                <p className="item-meta">{p.description}</p>
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