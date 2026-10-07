// Base configuration for the frontend API client.
//
// NEXT_PUBLIC_* environment variables are inlined at build time and can be
// set in a local .env.local file.
//
// Production defaults to a relative base ("") because the deployed site is
// served by the API itself: same origin, so no CORS_ORIGINS entry and no
// NEXT_PUBLIC_API_URL are needed. Only `next dev`, where the page is served by
// Next on :3000, falls back to the local backend URL.

const EXPLICIT_BASE = process.env.NEXT_PUBLIC_API_URL;

export const API_BASE_URL = (
  EXPLICIT_BASE ??
  (process.env.NODE_ENV === "development" ? "http://localhost:8000" : "")
).replace(/\/+$/, "");

/** Error thrown by requestJson with a message that is safe to show a user. */
export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function readErrorDetail(response: Response): Promise<string | null> {
  // FastAPI returns {"detail": ...} for 4xx/5xx. The body itself may be
  // missing or malformed, so parsing is defensive on purpose.
  try {
    const body: unknown = await response.json();
    if (body && typeof body === "object" && "detail" in body) {
      const detail = (body as { detail: unknown }).detail;
      if (typeof detail === "string") return detail;
    }
  } catch {
    // Fall through to the generic message below.
  }
  return null;
}

/**
 * Fetch JSON from the backend with uniform, user-safe error handling.
 *
 * Handles three failure modes that otherwise reached components raw: the
 * backend being offline (fetch rejects), a non-2xx status, and a 2xx response
 * whose body is not the JSON we expect.
 */
export async function requestJson<T>(
  path: string,
  init?: RequestInit,
  context = "Request"
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, init);
  } catch {
    throw new ApiError(
      "Cannot reach the AMUCS Nexus server. Check your connection and try again.",
      0
    );
  }

  if (!response.ok) {
    const detail = await readErrorDetail(response);
    throw new ApiError(
      detail ?? `${context} failed (${response.status})`,
      response.status
    );
  }

  try {
    return (await response.json()) as T;
  } catch {
    throw new ApiError(
      `${context} returned an unreadable response.`,
      response.status
    );
  }
}