// Health service: talks to the backend health endpoint.
//
// This shows the client/server pattern: the browser (client) sends an HTTP
// request to the FastAPI server and reads the JSON response.

import { requestJson } from "@/lib/api";
import type { HealthResponse } from "@/types";

export async function getHealth(): Promise<HealthResponse> {
  return requestJson<HealthResponse>("/api/health", undefined, "Health check");
}