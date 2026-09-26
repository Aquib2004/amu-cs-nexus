// Chat API: official AMU questions or one token-protected private upload.

import { API_BASE_URL } from "@/lib/api";
import type { ChatResponse, ChatUpload } from "@/types";

export async function askQuestion(question: string, upload?: ChatUpload | null): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      limit: 8,
      ...(upload ? { upload_id: upload.id, upload_token: upload.access_token } : {}),
    }),
  });
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(body?.detail ?? `Chat request failed: ${response.status}`);
  }
  return (await response.json()) as ChatResponse;
}

export async function uploadChatFile(file: File): Promise<ChatUpload> {
  const form = new FormData();
  form.append("file", file);
  const response = await fetch(`${API_BASE_URL}/api/chat/uploads`, { method: "POST", body: form });
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(body?.detail ?? `Upload failed: ${response.status}`);
  }
  return (await response.json()) as ChatUpload;
}

export async function deleteChatFile(upload: ChatUpload): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/chat/uploads/${upload.id}`, {
    method: "DELETE",
    headers: { "X-Upload-Token": upload.access_token },
  });
  if (!response.ok) throw new Error("Could not remove the uploaded file.");
}
