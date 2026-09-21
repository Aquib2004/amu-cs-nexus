// Research service: talks to the /api/research endpoint.

import { API_BASE_URL } from "@/lib/api";
import type { DocumentListItem } from "@/types/directory";

export async function getResearch(limit = 20): Promise<DocumentListItem[]> {
  const response = await fetch(`${API_BASE_URL}/api/research?limit=${limit}`);
  if (!response.ok) {
    throw new Error(
      `Failed to load research: ${response.status} ${response.statusText}`
    );
  }
  return (await response.json()) as DocumentListItem[];
}