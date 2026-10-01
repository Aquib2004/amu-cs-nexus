// Laboratories service: talks to the /api/laboratories endpoint.

import { requestJson } from "@/lib/api";
import type { LaboratoryRead } from "@/types/directory";

export async function getLaboratories(limit = 50): Promise<LaboratoryRead[]> {
  return requestJson<LaboratoryRead[]>(`/api/laboratories?limit=${limit}`, undefined, "Loading laboratories");
}