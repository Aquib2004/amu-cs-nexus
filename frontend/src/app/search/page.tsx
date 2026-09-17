"use client";

import { useState } from "react";

import { search } from "@/services/search";
import type { SearchResult } from "@/types";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [searched, setSearched] = useState(false);

  async function onSearch() {
    const q = query.trim();
    if (!q) return;
    setError(null);
    setSearched(true);
    try {
      setResults(await search({ q, limit: 20 }));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  }

  return (
    <main>
      <h1>Search</h1>
      <form
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
        />
        <button type="submit">Search</button>
      </form>

      {error ? (
        <p className="error">{error}</p>
      ) : searched && results.length === 0 ? (
        <p>No matching results.</p>
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
            </li>
          ))}
        </ol>
      )}
    </main>
  );
}