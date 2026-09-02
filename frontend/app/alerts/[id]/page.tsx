"use client";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { SeverityBadge } from "@/components/severity-badge";
import { useAuth } from "@/features/auth/auth-provider";
import { authenticatedGet } from "@/lib/api";
import type { AlertDetail } from "@/types/security";

export default function AlertDetailPage() {
  const { id } = useParams<{id:string}>(); const { token } = useAuth(); const [alert, setAlert] = useState<AlertDetail | null>(null);
  useEffect(() => { if (token) void authenticatedGet<AlertDetail>(`/api/v1/alerts/${id}`, token).then(setAlert); }, [id, token]);
  if (!alert) return <p className="empty">Loading alert…</p>;
  return <><header className="page-header"><div><p className="eyebrow">Alert investigation</p><h1>{alert.title}</h1><p>{alert.description}</p></div><SeverityBadge severity={alert.severity} /></header><section className="metrics detail-metrics"><article><span>Risk score</span><strong>{alert.risk_score}</strong></article><article><span>Status</span><strong>{alert.status}</strong></article><article><span>Rule</span><strong className="small-value">{alert.detection_rule} v{alert.rule_version}</strong></article></section><section className="panel table-wrap"><div className="panel-title"><h2>Supporting evidence</h2><span>{alert.supporting_events.length} events</span></div><table><thead><tr><th>Time</th><th>Source IP</th><th>User</th><th>Outcome</th></tr></thead><tbody>{alert.supporting_events.map((event) => <tr key={event.id}><td>{new Date(event.timestamp).toLocaleString()}</td><td><code>{event.source_ip}</code></td><td>{event.user_identifier}</td><td>{event.outcome}</td></tr>)}</tbody></table></section></>;
}
