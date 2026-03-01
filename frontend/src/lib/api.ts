/**
 * API client for BharatPrice AI backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ChatRequest {
    message: string;
    user_id?: string;
    language?: string;
    region?: string;
    pincode?: string;
    state?: string;
    district?: string;
    session_id?: string;
}

export interface ChatResponse {
    reply: string;
    intent: string;
    language: string;
    suggestions: string[];
}

export async function sendChat(request: ChatRequest): Promise<ChatResponse> {
    const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
    });
    if (!res.ok) throw new Error("Chat API error");
    return res.json();
}

