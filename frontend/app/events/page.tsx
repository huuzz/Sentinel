"use client";
import { useEffect, useState } from "react";
import { useAuth } from "@/features/auth/auth-provider";
import { authenticatedGet } from "@/lib/api";
import type { SecurityEvent } from "@/types/security";

export default function EventsPage() {
  const { token } = useAuth(); const [events, setEvents] = useState<SecurityEvent[]>([]);
  useEffect(() => { if (token) void authenticatedGet<{items:SecurityEvent[]}>("/api/v1/events?limit=100", token).then(data => setEvents(data.items)); }, [token]);
  return <><header className="page-header"><div><p className="eyebrow">Telemetry</p><h1>Security events</h1><p>Validated activity with advisory anomaly scoring. ML scores never create alerts.</p></div></header><section className="panel table-wrap"><table><thead><tr><th>Time</th><th>Type</th><th>Outcome</th><th>Source IP</th><th>User</th><th>Anomaly</th><th>Source</th></tr></thead><tbody>{events.map((event) => <tr key={event.id}><td>{new Date(event.timestamp).toLocaleString()}</td><td>{event.event_type}</td><td>{event.outcome ?? "—"}</td><td><code>{event.source_ip ?? "—"}</code></td><td>{event.user_identifier ?? "—"}</td><td><span className={event.is_anomaly?"anomaly high":"anomaly"}>{event.anomaly_score === null ? "Unavailable" : `${Math.round(event.anomaly_score*100)}%`}</span></td><td>{event.source}</td></tr>)}</tbody></table>{!events.length && <p className="empty">No events received yet.</p>}</section></>;
}
