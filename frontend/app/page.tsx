import Link from "next/link";
import { SeverityBadge } from "@/components/severity-badge";
import { StatusCard } from "@/components/status-card";
import { getBackendHealth, getDashboard } from "@/lib/api";

export default async function Dashboard() {
  const [health, summary] = await Promise.all([getBackendHealth(), getDashboard()]);
  const count = (name:string) => summary?.alerts_by_severity.find((item) => item.name === name)?.count ?? 0;
  return <><header className="page-header"><div><p className="eyebrow">Security operations</p><h1>Threat overview</h1><p>Current telemetry and rule-based findings across SentinelAI.</p></div><Link className="button" href="/events">View events</Link></header><section className="metrics"><article><span>Total events</span><strong>{summary?.total_events ?? "—"}</strong></article><article><span>Alerts today</span><strong>{summary?.alerts_today ?? "—"}</strong></article><article><span>Critical</span><strong className="critical-text">{count("CRITICAL")}</strong></article><article><span>High</span><strong className="high-text">{count("HIGH")}</strong></article></section><StatusCard state={health} /><section className="panel"><div className="panel-title"><h2>Recent alerts</h2><Link href="/alerts">View all</Link></div>{summary?.recent_alerts.length ? <div className="alert-list">{summary.recent_alerts.map((alert) => <Link href={`/alerts/${alert.id}`} key={alert.id}><SeverityBadge severity={alert.severity} /><span><strong>{alert.title}</strong><small>{alert.detection_rule} · {new Date(alert.created_at).toLocaleString()}</small></span><b>{alert.risk_score}</b></Link>)}</div> : <p className="empty">No alerts yet. Run the safe brute-force simulator to generate the first finding.</p>}</section></>;
}
