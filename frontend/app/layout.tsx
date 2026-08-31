import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "SentinelAI", description: "Security monitoring and threat analysis" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
