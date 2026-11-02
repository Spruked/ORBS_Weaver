import { useEffect, useRef, useState } from "react";
import { isTauri } from "@tauri-apps/api/core";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { embodimentSession } from './session';

const endpoint = "http://127.0.0.1:16521";
type Connection = { llm_connected: boolean; models: string[]; tts_loaded: boolean };
type RecalledMemory = {atom_id: string; statement: string; status: string; priority: string; source_entry_ids: string[]; relationships: unknown[]};

export function Conversation() {
  const [connection, setConnection] = useState<Connection | null>(null);
  const [text, setText] = useState("");
  const [reply, setReply] = useState("");
  const [voice, setVoice] = useState(true);
  const [priority, setPriority] = useState("low");
  const [closeReport, setCloseReport] = useState("");
  const session = useRef<string | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const [audioUrl, setAudioUrl] = useState("");
  const [retained, setRetained] = useState(false);
  const [recalled, setRecalled] = useState<RecalledMemory[]>([]);
  const [searched, setSearched] = useState(false);
  const player = useRef<HTMLAudioElement>(null);
  const active = useRef<AbortController | null>(null);
  const mounted = useRef(true);

  useEffect(() => {
    const end = () => {
      const id = session.current;
      session.current = null;
      player.current?.pause();
      setReply(""); setAudioUrl(""); setText(""); setRecalled([]); setSearched(false); setRetained(false);
      if (id) fetch(`${endpoint}/sessions/end`, {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({session_id:id}),keepalive:true}).catch(() => {});
    };
    window.addEventListener("orbot:end-session", end);
    const suspend = () => { player.current?.pause(); active.current?.abort(); };
    window.addEventListener("pagehide", suspend);
    return () => { window.removeEventListener("orbot:end-session", end); window.removeEventListener("pagehide", suspend); };
  }, []);

  useEffect(() => {
    mounted.current = true;
    const controller = new AbortController();
    fetch(`${endpoint}/status`, { signal: controller.signal })
      .then((response) => { if (!response.ok) throw new Error("Communication status unavailable"); return response.json(); })
      .then(setConnection).catch(() => setConnection(null));
    return () => { mounted.current = false; controller.abort(); active.current?.abort();
    };
  }, []);

  useEffect(() => () => { if (audioUrl) URL.revokeObjectURL(audioUrl); }, [audioUrl]);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (pending || !text.trim()) return;
    player.current?.pause();
    setAudioUrl(""); setError(""); setReply(""); setRetained(false); setCloseReport(""); setPending(true);
    const controller = new AbortController();
    active.current = controller;
    try {
      if (!session.current) session.current = await embodimentSession();
      const response = await fetch(`${endpoint}/conversation`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, speak: voice, session_id:session.current, priority }), signal: controller.signal,
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || "Conversation failed");
      if (!mounted.current) return;
      session.current = result.session_id;
      setReply(result.text);
      setRetained(Boolean(result.memory?.retained));
      setRecalled(result.recall?.results ?? []); setSearched(true);
      if (result.speech_error) setError(result.speech_error);
      if (result.audio_wav) {
        const data = Uint8Array.from(atob(result.audio_wav), (c) => c.charCodeAt(0));
        setAudioUrl(URL.createObjectURL(new Blob([data], { type: "audio/wav" })));
      }
    } catch (reason) {
      if (mounted.current) setError(reason instanceof Error ? reason.message : String(reason));
    } finally { if (mounted.current) setPending(false); }
  }

  async function recallOnly() {
    if (pending || !text.trim()) return;
    setPending(true); setError("");
    try {
      if (!session.current) session.current = await embodimentSession();
      const response = await fetch(`${endpoint}/memory/recall`, {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({session_id:session.current,query:text,limit:5})});
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || "Recall failed");
      setRecalled(result.results); setSearched(true);
    } catch (reason) { setError(String(reason)); }
    finally { setPending(false); }
  }

  return <article className="conversation">
    <span className="status">{connection?.llm_connected ? "Local llama.cpp connected" : "Communication offline or model unavailable"}</span>
    <h2>Talk to Orbot</h2>
    <p>Local language assistance · Deterministic governance remains separate</p>
    <form onSubmit={submit}>
      <label htmlFor="message">Message</label>
      <textarea id="message" value={text} onChange={(event) => setText(event.target.value)} maxLength={2000} required rows={3} />
      <label className="voice-option"><input type="checkbox" checked={voice} onChange={(event) => setVoice(event.target.checked)} /> Generate Qwen3-TTS voice</label>
      <label htmlFor="memory-priority">Memory importance</label>
      <select id="memory-priority" value={priority} onChange={event => setPriority(event.target.value)}>
        <option value="high">High — retain in AIMS</option>
        <option value="medium">Medium — SKG review at session close</option>
        <option value="low">Low — temporary unless repeated and graph-relevant</option>
      </select>
      <button type="submit" disabled={pending || !text.trim()}>{pending ? "Generating reply…" : "Send to local model"}</button>
      <button type="button" disabled={pending || !text.trim()} onClick={recallOnly}>Search saved AIMS memory</button>
    </form>
    {reply && <p className="reply" aria-live="polite">{reply}</p>}
    {retained && <p role="status">Saved to AIMS long-term memory.</p>}
    {searched && <details className="memory-recall"><summary>AIMS / SKG recall · {recalled.length} saved record{recalled.length === 1 ? "" : "s"}</summary>
      {recalled.length === 0 && <p>No matching retained records. Temporary session messages are not searched across sessions.</p>}
      {recalled.map(item => <section key={item.atom_id}>
        <p>{item.statement}</p><small>{item.priority} priority · Saved assertion · {item.status} · {item.relationships.length} graph relationships</small>
        <small>Source: {item.source_entry_ids.join(", ")}</small>
      </section>)}
    </details>}
    {audioUrl && <div><audio ref={player} src={audioUrl} controls aria-label="Orbot voice reply" />
      <button onClick={() => { if (player.current) { player.current.pause(); player.current.currentTime = 0; } }}>Stop voice</button></div>}
    {error && <p role="alert">{error}</p>}
    <button disabled={pending} onClick={async () => {
      try {
        if (session.current) { const response = await fetch(`${endpoint}/sessions/end`, {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({session_id:session.current})}); if (!response.ok) throw new Error("Could not close session"); const data=await response.json(); const review=data.close_review; if (review) setCloseReport(`SKG review: ${review.saved} saved, ${review.pruned} pruned, ${review.duplicates} duplicates skipped. ${review.retained_high} High-priority records retained.`); }
        session.current = null; setReply(""); setText(""); setAudioUrl(""); setError(""); setRecalled([]); setSearched(false); setRetained(false);
      } catch (reason) { setError(String(reason)); }
    }}>End session and clear short-term memory</button>
    {closeReport && <p role="status">{closeReport}</p>}
    <small>Three session caches. SKG closing review completes before purge. No tool or motion authority.</small>
  </article>;
}
