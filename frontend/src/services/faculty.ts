// Faculty service: talks to the /api/faculty endpoints.

import { requestJson } from "@/lib/api";
import type { FacultyMember } from "@/types/directory";

export async function getFaculty(
  department?: string
): Promise<FacultyMember[]> {
  const query = new URLSearchParams();
  if (department) query.set("department", department);
  return requestJson<FacultyMember[]>(`/api/faculty?${query.toString()}`, undefined, "Loading faculty");
}