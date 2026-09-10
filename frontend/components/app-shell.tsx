"use client";
import Link from "next/link";
import type { ReactNode } from "react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/features/auth/auth-provider";

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname(); const { user, logout } = useAuth();
  if (pathname === "/login") return <main className="login-page">{children}</main>;
  return <div className="shell"><aside><Link className="brand" href="/"><span className="mark">S</span>Sentinel</Link><p className="side-label">Operations</p><nav><Link href="/">Overview</Link><Link href="/alerts">Alerts</Link><Link href="/events">Events</Link><Link href="/knowledge">Knowledge</Link>{user?.role === "ADMIN" && <Link href="/admin/users">Users</Link>}</nav><div className="side-footer">{user ? <><span>{user.email} · {user.role}</span><button onClick={() => void logout()}>Sign out</button></> : <><span className="pulse" /> Authenticating</>}</div></aside><main>{children}</main></div>;
}
