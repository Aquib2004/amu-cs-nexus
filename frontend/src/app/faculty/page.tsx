"use client";

import { useEffect, useState } from "react";

import { getFaculty } from "@/services/faculty";
import type { FacultyMember } from "@/types/directory";

export default function FacultyPage() {
  const [members, setMembers] = useState<FacultyMember[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getFaculty("computer-science")
      .then(setMembers)
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Unknown error")
      )
      .finally(() => setLoading(false));
  }, []);

  return (
    <main>
      <h1 className="page-title">Faculty</h1>
      <p className="page-subtitle">
        Faculty directory for the Department of Computer Science, loaded from
        the official AMU site.
      </p>
      {error ? (
        <p className="error">Could not load faculty: {error}</p>
      ) : loading ? (
        <p className="loading">Loading faculty&hellip;</p>
      ) : members.length === 0 ? (
        <div className="empty-state">No faculty records yet.</div>
      ) : (
        <ul className="item-list">
          {members.map((m) => (
            <li key={m.id} className="item-card">
              {m.image_url && (
                <img
                  className="faculty-photo"
                  src={m.image_url}
                  alt={`Photo of ${m.name}`}
                  loading="lazy"
                />
              )}
              <h2 className="item-title">{m.name}</h2>
              <div className="item-tags">
                <span className="badge">
                  {m.designation ?? m.title ?? "Faculty"}
                </span>
              </div>
              {Array.isArray(m.specializations) && m.specializations.length > 0 && (
                <div className="item-tags">
                  {m.specializations.map((s) => (
                    <span key={s} className="badge">
                      {s}
                    </span>
                  ))}
                </div>
              )}
              {m.email && (
                <p className="item-meta">
                  <a href={`mailto:${m.email}`}>{m.email}</a>
                </p>
              )}
              {m.phone && <p className="item-meta">{m.phone}</p>}
              {m.profile_url && (
                <a href={m.profile_url} target="_blank" rel="noreferrer">
                  Official profile
                </a>
              )}
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}