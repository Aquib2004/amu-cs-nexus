// Staff service: talks to the /api/staff endpoint.

import { requestJson } from "@/lib/api";
import type { StaffRead } from "@/types/directory";

export async function getStaff(limit = 50): Promise<StaffRead[]> {
  return requestJson<StaffRead[]>(`/api/staff?limit=${limit}`, undefined, "Loading staff");
}