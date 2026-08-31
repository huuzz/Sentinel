export type HealthState = { status: "ok"; service: string };

export async function getBackendHealth(): Promise<HealthState | null> {
  const baseUrl = process.env.BACKEND_INTERNAL_URL ?? "http://localhost:8000";
  try {
    const response = await fetch(`${baseUrl}/health/live`, { cache: "no-store", signal: AbortSignal.timeout(3000) });
    if (!response.ok) return null;
    return (await response.json()) as HealthState;
  } catch {
    return null;
  }
}
