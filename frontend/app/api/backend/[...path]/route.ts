import { NextRequest, NextResponse } from "next/server";

const backend = process.env.BACKEND_INTERNAL_URL ?? "http://localhost:8000";
const maxBodyBytes = 1_048_576;

async function boundedBody(request: NextRequest): Promise<string | undefined> {
  if (!request.body) return undefined;
  const reader = request.body.getReader();
  const decoder = new TextDecoder();
  let size = 0;
  let body = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    size += value.byteLength;
    if (size > maxBodyBytes) {
      await reader.cancel();
      throw new Error("request_too_large");
    }
    body += decoder.decode(value, { stream: true });
  }
  return body + decoder.decode();
}

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const url = new URL(`/api/v1/${path.join("/")}`, backend);
  url.search = request.nextUrl.search;
  const headers = new Headers();
  for (const name of ["authorization", "content-type", "cookie"]) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }
  let body: string | undefined;
  try {
    body = request.method === "GET" || request.method === "HEAD" ? undefined : await boundedBody(request);
  } catch {
    return NextResponse.json({ error: { code: "request_too_large", message: "Request body is too large" } }, { status: 413 });
  }
  const response = await fetch(url, { method: request.method, headers, body, cache: "no-store", signal: AbortSignal.timeout(30000) });
  const outgoing = new NextResponse(response.body, { status: response.status });
  const contentType = response.headers.get("content-type");
  const setCookie = response.headers.get("set-cookie");
  if (contentType) outgoing.headers.set("content-type", contentType);
  for (const name of ["retry-after", "x-request-id", "www-authenticate"]) {
    const value = response.headers.get(name);
    if (value) outgoing.headers.set(name, value);
  }
  if (setCookie) outgoing.headers.set("set-cookie", setCookie.replaceAll("Path=/api/v1/auth", "Path=/api/backend/auth"));
  return outgoing;
}

export const GET = proxy;
export const POST = proxy;
export const PATCH = proxy;
