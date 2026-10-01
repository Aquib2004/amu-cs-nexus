// Search service: calls the backend /api/search endpoint.

import { requestJson } from "@/lib/api";
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

  return requestJson<SearchResult[]>(`/api/search?${query.toString()}`, undefined, "Search");
}