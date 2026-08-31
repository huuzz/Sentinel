import { notFound } from "next/navigation";
import { SeverityBadge } from "@/components/severity-badge";
import { getAlert } from "@/lib/api";

export default async function AlertDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const alert = await getAlert(id);
  if (!alert) notFound();
  return <><header className="page-header"><div><p className="eyebrow">Alert investigation</p><h1>{alert.title}</h1><p>{alert.description}</p></div><SeverityBadge severity={alert.severity} /></header><section className="metrics detail-metrics"><article><span>Risk score</span><strong>{alert.risk_score}</strong></article><article><span>Status</span><strong>{alert.status}</strong></article><article><span>Rule</span><strong className="small-value">{alert.detection_rule} v{alert.rule_version}</strong></article></section><section className="panel table-wrap"><div className="panel-title"><h2>Supporting evidence</h2><span>{alert.supporting_events.length} events</span></div><table><thead><tr><th>Time</th><th>Source IP</th><th>User</th><th>Outcome</th></tr></thead><tbody>{alert.supporting_events.map((event) => <tr key={event.id}><td>{new Date(event.timestamp).toLocaleString()}</td><td><code>{event.source_ip}</code></td><td>{event.user_identifier}</td><td><span className="outcome failure">{event.outcome}</span></td></tr>)}</tbody></table></section></>;
}
