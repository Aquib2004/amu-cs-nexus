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

// Matches the sources returned by POST /api/chat on the backend.
export interface ChatSource {
  number: number;
  source_url: string;
  document_id: string;
  chunk_id: string;
  text: string;
}

// Matches the response from POST /api/chat on the backend.
export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
}