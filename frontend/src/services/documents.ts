// Documents service: talks to the /api/documents endpoints.

import { requestJson } from "@/lib/api";
import type { DocumentDetail, DocumentListItem } from "@/types/directory";

export interface DocumentListParams {
  limit?: number;
  offset?: number;
  document_type?: string;
  department?: string;
}

export async function getDocuments(
  params: DocumentListParams = {}
): Promise<DocumentListItem[]> {
  const query = new URLSearchParams();
  if (params.limit) query.set("limit", String(params.limit));
  if (params.offset) query.set("offset", String(params.offset));
  if (params.document_type) query.set("document_type", params.document_type);
  if (params.department) query.set("department", params.department);
  return requestJson<DocumentListItem[]>(`/api/documents?${query.toString()}`, undefined, "Loading documents");
}

export async function getDocument(id: string): Promise<DocumentDetail> {
  return requestJson<DocumentDetail>(`/api/documents/${id}`, undefined, "Loading document");
}