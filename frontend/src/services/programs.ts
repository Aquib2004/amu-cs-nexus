// Programs service: talks to the /api/programs endpoint.

import { requestJson } from "@/lib/api";
import type { ProgramRead } from "@/types/directory";

export async function getPrograms(limit = 50): Promise<ProgramRead[]> {
  return requestJson<ProgramRead[]>(`/api/programs?limit=${limit}`, undefined, "Loading programmes");
}