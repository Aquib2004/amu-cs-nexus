// Faculty service: talks to the /api/faculty endpoints.

import { API_BASE_URL } from "@/lib/api";
import type { FacultyMember } from "@/types/directory";

export async function getFaculty(
  department?: string
): Promise<FacultyMember[]> {
  const query = new URLSearchParams();
  if (department) query.set("department", department);
  const response = await fetch(
    `${API_BASE_URL}/api/faculty?${query.toString()}`
  );
  if (!response.ok) {
    throw new Error(
      `Failed to load faculty: ${response.status} ${response.statusText}`
    );
  }
  return (await response.json()) as FacultyMember[];
}