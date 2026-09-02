"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { SeverityBadge } from "@/components/severity-badge";
import { useAuth } from "@/features/auth/auth-provider";
import { authenticatedGet } from "@/lib/api";
import type { AIAnalysis, AlertDetail } from "@/types/security";

export default function AlertDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { token, user } = useAuth();
  const [alert, setAlert] = useState<AlertDetail | null>(null);
  const [analysis, setAnalysis] = useState<AIAnalysis | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  useEffect(() => {
    if (token) {
      void authenticatedGet<AlertDetail>(`/api/v1/alerts/${id}`, token).then(setAlert);
      void fetch(`/api/backend/alerts/${id}/analysis`, {
        headers: { Authorization: `Bearer ${token}` },
      }).then(async response => {
        if (response.ok) setAnalysis(await response.json());
      });
    }
  }, [id, token]);
  async function analyze() {
    if (!token) return;
    setAnalyzing(true);
    const response = await fetch(`/api/backend/alerts/${id}/analysis`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (response.ok) setAnalysis(await response.json());
    setAnalyzing(false);
  }
  if (!alert) return <p className="empty">Loading alert…</p>;
  const mayAnalyze = user?.role === "ADMIN" || user?.role === "ANALYST";
  return <><header className="page-header"><div><p className="eyebrow">Alert investigation</p><h1>{alert.title}</h1><p>{alert.description}</p></div><SeverityBadge severity={alert.severity} /></header><section className="metrics detail-metrics"><article><span>Risk score</span><strong>{alert.risk_score}</strong></article><article><span>Status</span><strong>{alert.status}</strong></article><article><span>Rule</span><strong className="small-value">{alert.detection_rule} v{alert.rule_version}</strong></article></section><section className="panel analysis-panel"><div className="panel-title"><h2>AI analyst</h2>{mayAnalyze && <button className="button" onClick={() => void analyze()} disabled={analyzing}>{analyzing ? "Analyzing…" : analysis ? "Analyze again" : "Analyze alert"}</button>}</div>{analysis ? <><p className="analysis-attack">{analysis.likely_attack} · {Math.round(analysis.confidence * 100)}% confidence</p><p>{analysis.summary}</p><h3>Recommended actions</h3><ol>{analysis.recommended_actions.map(action => <li key={action}>{action}</li>)}</ol><small>Advisory only · {analysis.provider} / {analysis.model}</small></> : <p className="empty">No analysis yet. Analysis is advisory and never performs remediation.</p>}</section><section className="panel table-wrap"><div className="panel-title"><h2>Supporting evidence</h2><span>{alert.supporting_events.length} events</span></div><table><thead><tr><th>Time</th><th>Source IP</th><th>User</th><th>Outcome</th></tr></thead><tbody>{alert.supporting_events.map(event => <tr key={event.id}><td>{new Date(event.timestamp).toLocaleString()}</td><td><code>{event.source_ip}</code></td><td>{event.user_identifier}</td><td>{event.outcome}</td></tr>)}</tbody></table></section></>;
}
