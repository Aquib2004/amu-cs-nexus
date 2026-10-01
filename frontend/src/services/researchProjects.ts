// Research projects service: talks to the /api/research-projects endpoint.

import { requestJson } from "@/lib/api";
import type { ResearchProjectRead } from "@/types/directory";

export async function getResearchProjects(
  limit = 50
): Promise<ResearchProjectRead[]> {
  return requestJson<ResearchProjectRead[]>(`/api/research-projects?limit=${limit}`, undefined, "Loading research projects");
}