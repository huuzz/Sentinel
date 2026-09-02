"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

type User = { id: string; email: string; role: "ADMIN" | "ANALYST" | "VIEWER"; is_active: boolean };
type Auth = { token: string | null; user: User | null; ready: boolean; login(email: string, password: string): Promise<void>; logout(): Promise<void> };
const AuthContext = createContext<Auth | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);
  const router = useRouter();
  const pathname = usePathname();
  const loadUser = useCallback(async (accessToken: string) => {
    const response = await fetch("/api/backend/auth/me", { headers: { Authorization: `Bearer ${accessToken}` } });
    if (!response.ok) throw new Error("Unable to load session");
    setUser(await response.json());
  }, []);
  const refresh = useCallback(async () => {
    const response = await fetch("/api/backend/auth/refresh", { method: "POST" });
    if (response.ok) { const body = await response.json(); setToken(body.access_token); await loadUser(body.access_token); }
    setReady(true);
  }, [loadUser]);
  // Session restoration is an external cookie-backed synchronization on first mount.
  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => { void refresh(); }, [refresh]);
  useEffect(() => { if (ready && !user && pathname !== "/login") router.replace("/login"); }, [pathname, ready, router, user]);
  async function login(email: string, password: string) {
    const response = await fetch("/api/backend/auth/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) });
    if (!response.ok) throw new Error("Invalid email or password");
    const body = await response.json(); setToken(body.access_token); await loadUser(body.access_token); router.replace("/");
  }
  async function logout() {
    if (token) await fetch("/api/backend/auth/logout", { method: "POST", headers: { Authorization: `Bearer ${token}` } });
    setToken(null); setUser(null); router.replace("/login");
  }
  return <AuthContext.Provider value={{ token, user, ready, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used within AuthProvider");
  return value;
}
