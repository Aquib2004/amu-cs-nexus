// Search service: calls the backend /api/search endpoint.

import { API_BASE_URL } from "@/lib/api";
import type { SearchResult } from "@/types";

export interface SearchParams {
  q: string;
  limit?: number;
  department?: string;
  document_type?: string;
}

export async function search(params: SearchParams): Promise<SearchResult[]> {
  const query = new URLSearchParams({
    q: params.q,
    limit: String(params.limit ?? 10),
  });
  if (params.department) query.set("department", params.department);
  if (params.document_type) query.set("document_type", params.document_type);

  const response = await fetch(`${API_BASE_URL}/api/search?${query.toString()}`);
  if (!response.ok) {
    throw new Error(
      `Search failed: ${response.status} ${response.statusText}`
    );
  }
  return (await response.json()) as SearchResult[];
}