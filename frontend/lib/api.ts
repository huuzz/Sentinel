import type { Alert, AlertDetail, DashboardSummary, SecurityEvent } from "@/types/security";

export type HealthState = { status: "ok"; service: string };
const baseUrl = process.env.BACKEND_INTERNAL_URL ?? "http://localhost:8000";

async function apiGet<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${baseUrl}${path}`, { cache: "no-store", signal: AbortSignal.timeout(3000) });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch { return null; }
}

export async function getBackendHealth(): Promise<HealthState | null> {
  return apiGet<HealthState>("/health/live");
}

export const getDashboard = () => apiGet<DashboardSummary>("/api/v1/dashboard/summary");
export const getEvents = async () => (await apiGet<{items:SecurityEvent[]}>("/api/v1/events?limit=100"))?.items ?? [];
export const getAlerts = async () => (await apiGet<{items:Alert[]}>("/api/v1/alerts?limit=100"))?.items ?? [];
export const getAlert = (id:string) => apiGet<AlertDetail>(`/api/v1/alerts/${encodeURIComponent(id)}`);
