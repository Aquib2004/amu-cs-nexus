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
      <h1>Faculty</h1>
      <p className="chat-hint">
        Faculty directory for the Department of Computer Science. Source data
        is seeded locally for development.
      </p>
      {error ? (
        <p className="error">Could not load faculty: {error}</p>
      ) : loading ? (
        <p>Loading faculty…</p>
      ) : members.length === 0 ? (
        <p>No faculty records yet.</p>
      ) : (
        <ul className="directory-list">
          {members.map((m) => (
            <li key={m.id} className="directory-item">
              <strong>{m.name}</strong>
              <span className="notice-meta">
                {m.title ?? m.designation ?? "Faculty"}
              </span>
              <p className="directory-sub">
                {m.specializations.join(", ")}
              </p>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}