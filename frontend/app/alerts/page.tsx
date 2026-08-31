import Link from "next/link";
import { SeverityBadge } from "@/components/severity-badge";
import { getAlerts } from "@/lib/api";

export default async function AlertsPage() {
  const alerts = await getAlerts();
  return <><header className="page-header"><div><p className="eyebrow">Detection</p><h1>Alerts</h1><p>Deterministic findings that require analyst review.</p></div></header><section className="panel table-wrap"><table><thead><tr><th>Severity</th><th>Title</th><th>Rule</th><th>Risk</th><th>Status</th><th>Time</th></tr></thead><tbody>{alerts.map((alert) => <tr key={alert.id}><td><SeverityBadge severity={alert.severity} /></td><td><Link href={`/alerts/${alert.id}`}>{alert.title}</Link></td><td><code>{alert.detection_rule}</code></td><td>{alert.risk_score}</td><td>{alert.status}</td><td>{new Date(alert.created_at).toLocaleString()}</td></tr>)}</tbody></table>{!alerts.length && <p className="empty">No alerts detected.</p>}</section></>;
}
