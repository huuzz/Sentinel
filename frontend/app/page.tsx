"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { SeverityBadge } from "@/components/severity-badge";
import { StatusCard } from "@/components/status-card";
import { useAuth } from "@/features/auth/auth-provider";
import { authenticatedGet } from "@/lib/api";
import type { DashboardSummary } from "@/types/security";

export default function Dashboard() {
  const { token, ready } = useAuth(); const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [error, setError] = useState(false);
  useEffect(() => {
    let active = true;
    if (token) void authenticatedGet<DashboardSummary>("/api/v1/dashboard/summary", token)
      .then((data) => { if (active) setSummary(data); })
      .catch(() => { if (active) setError(true); });
    return () => { active = false; };
  }, [token]);
  if (!ready || !token) return <p className="empty">Loading secure session…</p>;
  if (error) return <section role="alert"><h1>Dashboard unavailable</h1><p>Could not retrieve current telemetry. Check the backend and refresh to retry.</p><button className="button" onClick={() => window.location.reload()}>Retry</button></section>;
  if (!summary) return <p className="empty" role="status">Loading telemetry…</p>;
  const count = (name:string) => summary?.alerts_by_severity.find((item) => item.name === name)?.count ?? 0;
  return <><header className="page-header"><div><p className="eyebrow">Security operations</p><h1>Threat overview</h1><p>Current telemetry and rule-based findings across SentinelAI.</p></div><Link className="button" href="/events">View events</Link></header><section className="metrics"><article><span>Total events</span><strong>{summary?.total_events ?? "—"}</strong></article><article><span>Alerts today</span><strong>{summary?.alerts_today ?? "—"}</strong></article><article><span>Critical</span><strong className="critical-text">{count("CRITICAL")}</strong></article><article><span>High</span><strong className="high-text">{count("HIGH")}</strong></article></section><StatusCard state={{status:"ok",service:"sentinel-api"}} /><section className="panel"><div className="panel-title"><h2>Detection coverage</h2><span>{summary?.alerts_by_rule.length ?? 0} triggered rules</span></div><div className="rule-breakdown">{summary?.alerts_by_rule.map(item => <div key={item.name}><code>{item.name}</code><strong>{item.count}</strong></div>)}</div></section><section className="panel"><div className="panel-title"><h2>Recent alerts</h2><Link href="/alerts">View all</Link></div>{summary?.recent_alerts.length ? <div className="alert-list">{summary.recent_alerts.map((alert) => <Link href={`/alerts/${alert.id}`} key={alert.id}><SeverityBadge severity={alert.severity} /><span><strong>{alert.title}</strong><small>{alert.detection_rule} · {new Date(alert.created_at).toLocaleString()}</small></span><b>{alert.risk_score}</b></Link>)}</div> : <p className="empty">No alerts yet.</p>}</section></>;
}
