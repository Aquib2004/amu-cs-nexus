// Research projects service: talks to the /api/research-projects endpoint.

import { API_BASE_URL } from "@/lib/api";
import type { ResearchProjectRead } from "@/types/directory";

export async function getResearchProjects(
  limit = 50
): Promise<ResearchProjectRead[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/research-projects?limit=${limit}`
  );
  if (!response.ok) {
    throw new Error(
      `Failed to load research projects: ${response.status} ${response.statusText}`
    );
  }
  return (await response.json()) as ResearchProjectRead[];
}