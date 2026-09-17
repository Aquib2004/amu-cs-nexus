// Shared TypeScript types used by the frontend.

// Matches the JSON returned by GET /api/health on the backend.
export interface HealthResponse {
  status: string;
  application: string;
  version: string;
  environment: string;
}

// Matches one item returned by GET /api/notices on the backend.
export interface Notice {
  id: string;
  title: string;
  url: string;
  category: string | null;
  published_at: string | null;
}

// Matches one item returned by GET /api/search on the backend.
export interface SearchResult {
  chunk_id: string;
  document_id: string;
  text: string;
  source_url: string;
  score: number;
}

