// Chat service: posts a question to the backend /api/chat endpoint.

import { API_BASE_URL } from "@/lib/api";
import type { ChatResponse } from "@/types";

export async function askQuestion(question: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, limit: 5 }),
  });

  if (!response.ok) {
    throw new Error(`Chat request failed: ${response.status} ${response.statusText}`);
  }
  return (await response.json()) as ChatResponse;
}
