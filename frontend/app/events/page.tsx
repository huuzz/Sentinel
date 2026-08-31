import { getEvents } from "@/lib/api";

export default async function EventsPage() {
  const events = await getEvents();
  return <><header className="page-header"><div><p className="eyebrow">Telemetry</p><h1>Security events</h1><p>Validated raw activity received by SentinelAI.</p></div></header><section className="panel table-wrap"><table><thead><tr><th>Time</th><th>Type</th><th>Outcome</th><th>Source IP</th><th>User</th><th>Source</th></tr></thead><tbody>{events.map((event) => <tr key={event.id}><td>{new Date(event.timestamp).toLocaleString()}</td><td>{event.event_type}</td><td><span className={`outcome ${event.outcome}`}>{event.outcome ?? "—"}</span></td><td><code>{event.source_ip ?? "—"}</code></td><td>{event.user_identifier ?? "—"}</td><td>{event.source}{event.simulated && <small className="simulated">simulated</small>}</td></tr>)}</tbody></table>{!events.length && <p className="empty">No events received yet.</p>}</section></>;
}
