export type Severity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type AlertStatus = "OPEN" | "INVESTIGATING" | "RESOLVED" | "DISMISSED";
export interface SecurityEvent { id:string; timestamp:string; event_type:string; source:string; outcome:string|null; user_identifier:string|null; source_ip:string|null; endpoint:string|null; status_code:number|null; simulated:boolean; metadata:Record<string,unknown>; }
export interface Alert { id:string; title:string; description:string; severity:Severity; status:AlertStatus; risk_score:number; detection_rule:string; rule_version:string; created_at:string; }
export interface AlertDetail extends Alert { supporting_events:SecurityEvent[] }
export interface DashboardSummary { total_events:number; alerts_today:number; alerts_by_severity:{name:string;count:number}[]; alerts_by_rule:{name:string;count:number}[]; common_event_types:{name:string;count:number}[]; event_volume:{timestamp:string;count:number}[]; recent_alerts:Alert[]; }
export interface AIAnalysis { id:string; alert_id:string; summary:string; likely_attack:string; confidence:number; evidence_references:string[]; recommended_actions:string[]; provider:string; model:string; created_at:string; }
