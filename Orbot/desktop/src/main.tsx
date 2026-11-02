import { StrictMode, useState, useRef, useEffect, type CSSProperties } from "react";
import { createRoot } from "react-dom/client";
import { invoke, isTauri } from "@tauri-apps/api/core";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { listen } from "@tauri-apps/api/event";
import type { Orb3D, OrbShape, OrbVisualState } from "./orb3d";
import { OrbVoice } from "./voice";
import "./styles.css";



function App() {
  const [error, setError] = useState("");
  const [menu, setMenu] = useState(false);
  const [voiceState, setVoiceState] = useState("idle");
  const [diameter, setDiameter] = useState(200);
  const [settings, setSettings] = useState({standard_diameter:240, minimum_diameter:80, maximum_diameter:350, auto_resize:true, resize_smoothness:.6, shape:"sphere" as OrbShape, shape_variation:false, shape_frequency:"occasional"});
  const [activeShape, setActiveShape] = useState<OrbShape>("sphere");
  const [settingsRevision, setSettingsRevision] = useState<string | null>(null);
  const [gaze, setGaze] = useState({x:0,y:0});
  const [motionAuthority, setMotionAuthority] = useState("ambient");
  const orbHost = useRef<HTMLDivElement | null>(null);
  const orb3d = useRef<Orb3D | null>(null);
  const diameterRef = useRef(diameter);
  useEffect(() => {
    if (!isTauri()) return;
    let active=true, timer=0;
    const load=async () => {
      try {
        const result=await invoke<{value:typeof settings,entry_id:string}>("presentation_preferences");
        if (active) {setSettings(result.value);setActiveShape(result.value.shape);setSettingsRevision(result.entry_id);}
      } catch { /* Keep the last applied values; Dock reports an unavailable Vault. */ }
      if (active) timer=window.setTimeout(load, 2000);
    };
    void load();
    return () => {active=false; window.clearTimeout(timer);};
  }, []);
  useEffect(() => {
    let live=true;
    void import("./orb3d").then(module=>module.Orb3D.create(orbHost.current!)).then(instance=>{if(live){orb3d.current=instance;instance.setShape(activeShape);instance.setState(voiceState as OrbVisualState);instance.setGaze(gaze.x,gaze.y);}else instance.dispose();}).catch(reason=>setError(`3D Orb renderer unavailable: ${String(reason)}`));
    return()=>{live=false;orb3d.current?.dispose();orb3d.current=null;};
  }, []);
  useEffect(()=>{orb3d.current?.setState(voiceState as OrbVisualState);},[voiceState]);
  useEffect(()=>{orb3d.current?.setShape(activeShape);},[activeShape]);
  useEffect(()=>{orb3d.current?.setGaze(gaze.x,gaze.y);},[gaze]);
  useEffect(()=>{
    if(!isTauri())return;
    let active=true;const stops:Promise<()=>void>[]=[];
    stops.push(listen<{x:number;y:number}>('orbot:gaze',event=>{if(active)setGaze(event.payload);}));
    stops.push(listen<{state:string;authority:string;velocity?:{x:number;y:number}}>('orbot:motion',event=>{
      if(!active)return;setMotionAuthority(event.payload.authority||"ambient");
    }));
    return()=>{active=false;stops.forEach(p=>void p.then(stop=>stop()));};
  },[]);
  const voice = useRef<OrbVoice | null>(null);
  if (!voice.current) voice.current = new OrbVoice(setVoiceState, setError);
  useEffect(() => {
    let active = true;
    const suspend = () => { void voice.current?.suspend().catch(reason => setError(String(reason))); };
    const subscriptions = isTauri() ? [
      listen<{device_id:string,label:string}>('orbot:input-device', event => {setError('');void voice.current?.selectInput(event.payload).catch(reason=>setError(String(reason)));}),
      listen('orbot:voice-control', event => {
        if(event.payload==='refresh_devices') {void voice.current?.publishInputs().catch(reason=>setError(String(reason)));return;}
        if(event.payload==='pause' || event.payload==='cancel') suspend();
        else if(event.payload==='start') {setError('');void voice.current?.startHandsFree().catch(reason=>setError(String(reason)));}
      }),
      listen<{offer?:boolean;observation?:{application:string;window_title:string;stable_seconds:number}}>('orbot:attention', event => {
        const observation=event.payload.observation;
        if(!event.payload.offer||!observation||voice.current?.state!=='listening')return;
        void invoke<{text:string;audio_wav:string}>('attention_offer',{
          application:observation.application,windowTitle:observation.window_title,stableSeconds:observation.stable_seconds
        }).then(result=>voice.current?.playAttentionOffer(result.audio_wav)).catch(reason=>{
          if(voice.current?.state==='listening')setError(`Orbot could not prepare the attention offer: ${String(reason)}`);
        });
      }),
      listen('orbot:shutdown', async () => {
        try { await voice.current?.endSession(); await invoke('shutdown_complete'); }
        catch (reason) { setError(String(reason)); }
      }),
    ] : [];
    if (isTauri()) void Promise.all(subscriptions).then(async () => { if (active) {await invoke('renderer_ready');await voice.current?.startHandsFree();} }).catch(reason => setError(String(reason)));
    window.addEventListener('pagehide', suspend);
    return () => { active = false; suspend(); window.removeEventListener('pagehide', suspend); subscriptions.forEach(p => { void p.then(stop => stop()); }); };
  }, []);
  const down = useRef<{x: number; y: number} | null>(null);
  const dragged = useRef(false);
  useEffect(() => {
    if (!isTauri()) return;
    let live=true, timer=0, last=performance.now();
    const reduced=window.matchMedia("(prefers-reduced-motion: reduce)");
    const tick=async () => {
      const now=performance.now(), dt=Math.min((now-last)/1000, 0.25); last=now;
      const target=Math.min(settings.maximum_diameter, Math.max(settings.minimum_diameter, settings.standard_diameter*(settings.auto_resize && ["thinking","speaking"].includes(voiceState) ? 1.15 : 1)));
      const tau=.2+settings.resize_smoothness*1.6;
      const next=reduced.matches ? target : diameterRef.current+(target-diameterRef.current)*(1-Math.exp(-dt/tau));
      try {
        const applied=await invoke<number>("resize_presentation", {diameter: next, panel: Boolean(menu || error)});
        if (live) { diameterRef.current=Math.abs(applied-next) <= 2 ? next : applied; setDiameter(applied); }
      } catch (reason) { if (live) setError(String(reason)); }
      if (live) timer=window.setTimeout(tick, 50);
    };
    void tick();
    return () => {live=false; window.clearTimeout(timer);};
  }, [settings, voiceState, menu, error]);
  async function saveSettings(patch:Partial<typeof settings>){
    const next={...settings,...patch};
    try{
      const result=await invoke<{value:typeof settings;entry_id:string}>("save_presentation_preferences",{value:next,expectedEntryId:settingsRevision});
      setSettings(result.value);if(patch.shape)setActiveShape(patch.shape);setSettingsRevision(result.entry_id);setError("");
    }catch(reason){setError(`Could not save Orb appearance settings: ${String(reason)}. Reload settings before retrying.`);}
  }
  async function setAuthority(authority:string){
    try{await invoke("set_motion_authority",{authority});setMotionAuthority(authority);setError("");}
    catch(reason){setError(`Could not change movement state: ${String(reason)}`);}
  }
  async function talk() { setError(""); await voice.current?.toggle(); }
  async function dock() {
    try {
      if (!isTauri()) throw new Error("Docking requires the native Orbot and Dock Station applications.");
      await invoke("dock_to_station");
      setMenu(false); setError("");
    } catch (reason) { setError(String(reason)); }
  }
  const gazeStyle={"--gaze-x":gaze.x,"--gaze-y":gaze.y} as CSSProperties;
  return <main className="floating">
    <button className="orb" style={{width: diameter, height: diameter}} data-voice-state={voiceState} aria-label={`Orbot voice: ${voiceState}`} title="Speak to Orbot; interrupt speech by speaking or clicking; click to pause/resume listening; right-click to dock"
      onClick={() => { if (!dragged.current) talk().catch((reason) => setError(String(reason))); }}
      onContextMenu={(event) => { event.preventDefault(); setMenu(!menu); }}
      onPointerDown={(event) => { if (event.button === 0) { down.current = {x: event.clientX, y: event.clientY}; dragged.current = false; event.currentTarget.setPointerCapture(event.pointerId); } }}
      onPointerMove={(event) => {
        if (down.current && Math.hypot(event.clientX-down.current.x, event.clientY-down.current.y)>5) {
          dragged.current = true;
          if (isTauri()) void invoke("manual_drag_move",{offsetX:down.current.x,offsetY:down.current.y}).catch(reason=>setError(String(reason)));
        }
      }} onPointerUp={() => {
        if (dragged.current && down.current && isTauri()) void invoke("manual_drag_move",{offsetX:down.current.x,offsetY:down.current.y}).catch(reason=>setError(String(reason)));
        down.current = null;
      }}>
      <div className="orb-visual-stage" style={gazeStyle} aria-hidden="true">
        <div className="orb-orbit" data-state={voiceState}>
          <i /><i /><i />
        </div>
        <div className="orb-renderer-host" ref={orbHost} />
      </div>
    </button>
    {menu && <div className="orb-menu"><button onClick={dock}>Dock to station</button>
      <label>Shape <select value={settings.shape} onChange={e=>void saveSettings({shape:e.target.value as OrbShape})}><option value="sphere">Sphere</option><option value="liquid">Liquid</option><option value="hexagon">Hexagon</option></select></label>
      <button onClick={()=>void setAuthority("hold")}>Hold position</button>
      <button onClick={()=>void setAuthority("guided")}>Guide near cursor</button>
      <button onClick={()=>void setAuthority("ambient")}>Resume ambient movement</button>
      <small>Movement: {motionAuthority}</small>
      <button onClick={() => setMenu(false)}>Close menu</button></div>}
    {error && <p role="alert">{error}</p>}
  </main>;
}
function Morb() {
  const [phase,setPhase]=useState("traveling");
  useEffect(() => { const subscription=listen<string>("orbot:morb-phase", event=>setPhase(event.payload)); return () => {void subscription.then(stop=>stop());}; }, []);
  return <div className="morb-halo" data-phase={phase}><div className="morb-core" /></div>;
}
const isMorb = isTauri() && getCurrentWindow().label.startsWith("morb-");
document.body.classList.toggle("morb-window", isMorb);
document.body.classList.toggle("orb-window", true);
document.documentElement.classList.toggle("orb-window", true);
createRoot(document.getElementById("root")!).render(<StrictMode>{isMorb ? <Morb /> : <App />}</StrictMode>);
