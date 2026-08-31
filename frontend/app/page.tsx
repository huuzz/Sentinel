import { StatusCard } from "@/components/status-card";
import { getBackendHealth } from "@/lib/api";

export default async function Home() {
  const health = await getBackendHealth();
  return (
    <main>
      <nav><strong><span className="mark">S</span> SentinelAI</strong><span>Foundation · Milestone 0</span></nav>
      <header><p className="eyebrow">Security operations platform</p><h1>See risk clearly.<br /><em>Respond deliberately.</em></h1><p className="lede">A secure, explainable foundation for collecting telemetry, detecting suspicious behavior, and helping analysts investigate.</p></header>
      <StatusCard state={health} />
      <section className="grid"><article><p className="number">01</p><h2>Deterministic first</h2><p>Security rules create alerts. AI and machine learning remain advisory and explainable.</p></article><article><p className="number">02</p><h2>Secure by design</h2><p>Untrusted telemetry is validated, bounded, and separated from trusted instructions.</p></article><article><p className="number">03</p><h2>Built to learn</h2><p>Clear boundaries and focused documentation make every architectural choice interview-ready.</p></article></section>
    </main>
  );
}
