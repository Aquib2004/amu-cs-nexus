// Staff service: talks to the /api/staff endpoint.

import { API_BASE_URL } from "@/lib/api";
import type { StaffRead } from "@/types/directory";

export async function getStaff(limit = 50): Promise<StaffRead[]> {
  const response = await fetch(`${API_BASE_URL}/api/staff?limit=${limit}`);
  if (!response.ok) {
    throw new Error(
      `Failed to load staff: ${response.status} ${response.statusText}`
    );
  }
  return (await response.json()) as StaffRead[];
}