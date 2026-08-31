import Link from "next/link";
import type { ReactNode } from "react";

export function AppShell({ children }: { children: ReactNode }) {
  return <div className="shell"><aside><Link className="brand" href="/"><span className="mark">S</span>SentinelAI</Link><p className="side-label">Operations</p><nav><Link href="/">Overview</Link><Link href="/alerts">Alerts</Link><Link href="/events">Events</Link></nav><div className="side-footer"><span className="pulse" /> Demo environment</div></aside><main>{children}</main></div>;
}
