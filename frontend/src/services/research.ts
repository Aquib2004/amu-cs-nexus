// Research service: talks to the /api/research endpoint.

import { requestJson } from "@/lib/api";
import type { DocumentListItem } from "@/types/directory";

export async function getResearch(limit = 20): Promise<DocumentListItem[]> {
  return requestJson<DocumentListItem[]>(`/api/research?limit=${limit}`, undefined, "Loading research");
}