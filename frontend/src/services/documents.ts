// Documents service: talks to the /api/documents endpoints.

import { API_BASE_URL } from "@/lib/api";
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
  const response = await fetch(`${API_BASE_URL}/api/documents?${query.toString()}`);
  if (!response.ok) {
    throw new Error(
      `Failed to load documents: ${response.status} ${response.statusText}`
    );
  }
  return (await response.json()) as DocumentListItem[];
}

export async function getDocument(id: string): Promise<DocumentDetail> {
  const response = await fetch(`${API_BASE_URL}/api/documents/${id}`);
  if (!response.ok) {
    throw new Error(
      `Failed to load document: ${response.status} ${response.statusText}`
    );
  }
  return (await response.json()) as DocumentDetail;
}