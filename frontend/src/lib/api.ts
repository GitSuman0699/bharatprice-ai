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
    session_id?: string;
}

export interface PriceInfo {
    source: string;
    price: number;
    unit: string;
}

export interface ChatResponse {
    reply: string;
    intent: string;
    language: string;
    prices?: PriceInfo[];
    audio_url?: string;
    suggestions: string[];
}

export interface PriceData {
    product_id: string;
    product_name: string;
    date: string;
    region: string;
    mandi_price: number;
    bigbasket_price: number;
    jiomart_price: number;
    local_avg: number;
    recommended_retail: number;
    demand_trend: string;
    unit: string;
}

export interface PriceTrend {
    product_name: string;
    region: string;
    period_days: number;
    current_price: number;
    price_change_pct: number;
    trend: string;
    data_points: { date: string; price: number }[];
    summary: string;
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

export async function getPrice(product: string, region = "delhi"): Promise<PriceData> {
    const res = await fetch(`${API_BASE}/api/prices/${encodeURIComponent(product)}?region=${region}`);
    if (!res.ok) throw new Error("Price API error");
    return res.json();
}

export async function getPriceTrend(product: string, region = "delhi", days = 30): Promise<PriceTrend> {
    const res = await fetch(`${API_BASE}/api/trends/${encodeURIComponent(product)}?region=${region}&days=${days}`);
    if (!res.ok) throw new Error("Trend API error");
    return res.json();
}

export async function getProducts(): Promise<{ products: { id: string; name: string; category: string }[] }> {
    const res = await fetch(`${API_BASE}/api/products`);
    if (!res.ok) throw new Error("Products API error");
    return res.json();
}

export async function getRegions(): Promise<{ regions: { id: string; city: string }[] }> {
    const res = await fetch(`${API_BASE}/api/regions`);
    if (!res.ok) throw new Error("Regions API error");
    return res.json();
}
