// Health service: talks to the backend health endpoint.
//
// This shows the client/server pattern: the browser (client) sends an HTTP
// request to the FastAPI server and reads the JSON response.

import { API_BASE_URL } from "@/lib/api";
import type { HealthResponse } from "@/types";

export async function getHealth(): Promise<HealthResponse> {
  // Send a GET request to the backend.
  const response = await fetch(`${API_BASE_URL}/api/health`);

  // A non-2xx status means something went wrong (e.g. 500, 404).
  if (!response.ok) {
    throw new Error(
      `Health check failed with status ${response.status} ${response.statusText}`
    );
  }

  // Parse the JSON response body into a typed object.
  return (await response.json()) as HealthResponse;
}
