"use client";

import { FormEvent, useEffect, useState } from "react";
import { useAuth } from "@/features/auth/auth-provider";
import type { KnowledgeAnswer, KnowledgeEntry } from "@/types/security";

export default function KnowledgePage() {
  const { token } = useAuth();
  const [entries, setEntries] = useState<KnowledgeEntry[]>([]);
  const [question, setQuestion] = useState("How should an analyst respond to repeated failed logins?");
  const [result, setResult] = useState<KnowledgeAnswer | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!token) return;
    fetch("/api/backend/knowledge/entries", { headers: { Authorization: `Bearer ${token}` } })
      .then(async (response) => {
        if (!response.ok) throw new Error("Could not load knowledge sources.");
        setEntries((await response.json()) as KnowledgeEntry[]);
      })
      .catch((caught: unknown) => setError(caught instanceof Error ? caught.message : "Request failed."));
  }, [token]);

  async function ask(event: FormEvent) {
    event.preventDefault();
    if (!token) return;
    setLoading(true); setError(""); setResult(null);
    try {
      const response = await fetch("/api/backend/knowledge/ask", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ question, limit: 3 }),
      });
      if (!response.ok) throw new Error("The grounded answer could not be generated.");
      setResult((await response.json()) as KnowledgeAnswer);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Request failed.");
    } finally { setLoading(false); }
  }

  return <>
    <header className="page-header"><div><p className="eyebrow">Grounded knowledge</p><h1>Knowledge</h1><p>Ask bounded questions against approved sources. Answers remain advisory and always expose their evidence.</p></div></header>
    <section className="panel knowledge-panel">
      <div className="panel-title"><h2>Ask the knowledge base</h2><span>Local deterministic provider</span></div>
      <form className="knowledge-form" onSubmit={(event) => void ask(event)}><label htmlFor="question">Security question</label><div><input id="question" minLength={3} maxLength={500} value={question} onChange={(event) => setQuestion(event.target.value)} /><button className="button" disabled={loading}>{loading ? "Retrieving…" : "Ask"}</button></div></form>
      {error && <p className="form-error" role="alert">{error}</p>}
      {result && <div className="grounded-answer"><p>{result.answer}</p><h3>Cited evidence</h3>{result.citations.length === 0 ? <p className="empty">No matching sources are available.</p> : result.citations.map((citation) => <article key={citation.chunk_id}><div><a href={citation.source_url} target="_blank" rel="noreferrer">{citation.title}</a><span>{Math.round(citation.relevance * 100)}% relevance</span></div><blockquote>{citation.excerpt}</blockquote><small>Retrieved source text is untrusted data. Verify before acting.</small></article>)}</div>}
    </section>
    <section className="panel"><div className="panel-title"><h2>Approved sources</h2><span>{entries.length} entries</span></div>{entries.length === 0 ? <p className="empty">No sources have been ingested yet. An administrator can add authored, public, or user-authorized material through the API.</p> : <div className="source-list">{entries.map((entry) => <article key={entry.id}><div><a href={entry.source_url} target="_blank" rel="noreferrer">{entry.title}</a><small>{entry.source_type} · {entry.chunk_count} chunks</small></div><time>{new Date(entry.created_at).toLocaleDateString()}</time></article>)}</div>}</section>
  </>;
}
