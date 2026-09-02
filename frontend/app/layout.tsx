import type { Metadata } from "next";
import "./globals.css";
import "./auth.css";
import { AppShell } from "@/components/app-shell";
import { AuthProvider } from "@/features/auth/auth-provider";

export const metadata: Metadata = { title: "SentinelAI", description: "Security monitoring and threat analysis" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><AuthProvider><AppShell>{children}</AppShell></AuthProvider></body></html>;
}
