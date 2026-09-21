"use client";

import { useState } from "react";

import { search } from "@/services/search";
import type { SearchResult } from "@/types";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  async function onSearch() {
    const q = query.trim();
    if (!q) return;
    setError(null);
    setSearched(true);
    setLoading(true);
    try {
      setResults(await search({ q, limit: 20 }));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1 className="page-title">Search</h1>
      <p className="page-subtitle">
        Keyword, semantic and hybrid search over indexed content.
      </p>
      <form
        className="field-row"
        onSubmit={(e) => {
          e.preventDefault();
          onSearch();
        }}
      >
        <label htmlFor="query">Search indexed content</label>
        <input
          id="query"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. computer vision"
          aria-label="Search query"
        />
        <button type="submit" className="btn" disabled={loading}>
          {loading ? "Searching…" : "Search"}
        </button>
      </form>

      {error ? (
        <p className="error">{error}</p>
      ) : loading ? (
        <p className="loading">Searching&hellip;</p>
      ) : searched && results.length === 0 ? (
        <div className="empty-state">No matching results.</div>
      ) : (
        <ol className="result-list">
          {results.map((r) => (
            <li key={r.chunk_id} className="result-item">
              <p>{r.text}</p>
              <a
                className="result-source"
                href={r.source_url}
                target="_blank"
                rel="noreferrer"
              >
                Source
              </a>
              <span className="result-score">score {r.score.toFixed(4)}</span>
            </li>
          ))}
        </ol>
      )}
    </main>
  );
}