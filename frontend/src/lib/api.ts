/**
 * API client for BharatPrice AI backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "";

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

/** Common headers sent with every API request. */
function getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
        "Content-Type": "application/json",
    };
    if (API_KEY) {
        headers["X-API-Key"] = API_KEY;
    }
    return headers;
}

export async function sendChat(request: ChatRequest): Promise<ChatResponse> {
    const res = await fetch(`${API_BASE}/api/chat`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify(request),
    });
    if (!res.ok) throw new Error("Chat API error");
    return res.json();
}
