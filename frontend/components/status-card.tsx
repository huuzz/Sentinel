import type { HealthState } from "@/lib/api";

export function StatusCard({ state }: { state: HealthState | null }) {
  const healthy = state?.status === "ok";
  return (
    <section className="status-card" aria-labelledby="system-status">
      <div><p className="eyebrow">System status</p><h2 id="system-status">{healthy ? "Operational" : "Unavailable"}</h2></div>
      <span className={healthy ? "status healthy" : "status unhealthy"}><span aria-hidden="true" />{state?.service ?? "Backend offline"}</span>
    </section>
  );
}
