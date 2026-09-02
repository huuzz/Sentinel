import { NextRequest, NextResponse } from "next/server";

const backend = process.env.BACKEND_INTERNAL_URL ?? "http://localhost:8000";

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const url = new URL(`/api/v1/${path.join("/")}`, backend);
  url.search = request.nextUrl.search;
  const headers = new Headers();
  for (const name of ["authorization", "content-type", "cookie"]) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }
  const response = await fetch(url, { method: request.method, headers, body: request.method === "GET" || request.method === "HEAD" ? undefined : await request.text(), cache: "no-store" });
  const outgoing = new NextResponse(response.body, { status: response.status });
  const contentType = response.headers.get("content-type");
  const setCookie = response.headers.get("set-cookie");
  if (contentType) outgoing.headers.set("content-type", contentType);
  if (setCookie) outgoing.headers.set("set-cookie", setCookie.replaceAll("Path=/api/v1/auth", "Path=/api/backend/auth"));
  return outgoing;
}

export const GET = proxy;
export const POST = proxy;
export const PATCH = proxy;
