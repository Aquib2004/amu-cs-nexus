// Chat API: official AMU questions or one token-protected private upload.

import { requestJson } from "@/lib/api";
import type { ChatResponse, ChatUpload } from "@/types";

export async function askQuestion(question: string, upload?: ChatUpload | null): Promise<ChatResponse> {
  return requestJson<ChatResponse>(
    "/api/chat",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        limit: 8,
        ...(upload ? { upload_id: upload.id, upload_token: upload.access_token } : {}),
      }),
    },
    "Chat request"
  );
}

export async function uploadChatFile(file: File): Promise<ChatUpload> {
  const form = new FormData();
  form.append("file", file);
  return requestJson<ChatUpload>("/api/chat/uploads", { method: "POST", body: form }, "Upload");
}

export async function deleteChatFile(upload: ChatUpload): Promise<void> {
  const response = await requestJson<Record<string, never>>(
    `/api/chat/uploads/${upload.id}`,
    { method: "DELETE", headers: { "X-Upload-Token": upload.access_token } },
    "Removing the uploaded file"
  );
  void response;
}