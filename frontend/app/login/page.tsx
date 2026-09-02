"use client";

import { FormEvent, useState } from "react";
import { useAuth } from "@/features/auth/auth-provider";

export default function LoginPage() {
  const { login } = useAuth(); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError(""); const data = new FormData(event.currentTarget);
    try { await login(String(data.get("email")), String(data.get("password"))); } catch (reason) { setError(reason instanceof Error ? reason.message : "Login failed"); setBusy(false); }
  }
  return <section className="login-card"><p className="eyebrow">Secure console</p><h1>Sign in to SentinelAI</h1><p>Use an administrator-managed account.</p><form onSubmit={submit}><label>Email<input name="email" type="email" autoComplete="username" required /></label><label>Password<input name="password" type="password" autoComplete="current-password" minLength={8} required /></label>{error && <p className="form-error" role="alert">{error}</p>}<button className="button" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button></form></section>;
}
