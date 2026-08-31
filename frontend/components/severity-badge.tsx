import type { Severity } from "@/types/security";
export function SeverityBadge({ severity }: { severity: Severity }) { return <span className={`badge severity-${severity.toLowerCase()}`}>{severity}</span>; }
