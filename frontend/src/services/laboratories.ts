// Laboratories service: talks to the /api/laboratories endpoint.

import { API_BASE_URL } from "@/lib/api";
import type { LaboratoryRead } from "@/types/directory";

export async function getLaboratories(limit = 50): Promise<LaboratoryRead[]> {
  const response = await fetch(`${API_BASE_URL}/api/laboratories?limit=${limit}`);
  if (!response.ok) {
    throw new Error(
      `Failed to load laboratories: ${response.status} ${response.statusText}`
    );
  }
  return (await response.json()) as LaboratoryRead[];
}