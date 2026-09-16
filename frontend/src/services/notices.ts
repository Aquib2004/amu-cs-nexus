// Notices service: talks to the backend notices endpoint.
//
// The browser (client) sends a GET to FastAPI, and we read the JSON list.

import { API_BASE_URL } from "@/lib/api";
import type { Notice } from "@/types";

export interface NoticeListParams {
  limit?: number;
  offset?: number;
}

export async function getNotices(
  params: NoticeListParams = {}
): Promise<Notice[]> {
  // Build the query string from optional parameters (e.g. ?limit=50).
  const query = new URLSearchParams();
  if (params.limit) query.set("limit", String(params.limit));
  if (params.offset) query.set("offset", String(params.offset));

  const url = `${API_BASE_URL}/api/notices?${query.toString()}`;
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(
      `Failed to load notices: ${response.status} ${response.statusText}`
    );
  }

  return (await response.json()) as Notice[];
}
