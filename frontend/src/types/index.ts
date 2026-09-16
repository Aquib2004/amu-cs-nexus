// Shared TypeScript types used by the frontend.

// Matches the JSON returned by GET /api/health on the backend.
export interface HealthResponse {
  status: string;
  application: string;
  version: string;
  environment: string;
}
