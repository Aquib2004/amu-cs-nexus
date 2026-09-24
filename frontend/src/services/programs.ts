// Programs service: talks to the /api/programs endpoint.

import { API_BASE_URL } from "@/lib/api";
import type { ProgramRead } from "@/types/directory";

export async function getPrograms(limit = 50): Promise<ProgramRead[]> {
  const response = await fetch(`${API_BASE_URL}/api/programs?limit=${limit}`);
  if (!response.ok) {
    throw new Error(
      `Failed to load programmes: ${response.status} ${response.statusText}`
    );
  }
  return (await response.json()) as ProgramRead[];
}