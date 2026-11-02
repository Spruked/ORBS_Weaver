import { embodimentSession } from './session';
import { VoiceActivity } from './voice_activity';
import { invoke, isTauri } from '@tauri-apps/api/core';
const gateway = 'http://127.0.0.1:16521';
async function post(path: string, body: object, signal?: AbortSignal) {
  const response = await fetch(gateway + path, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal});
  const result = await response.json();
  if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : JSON.stringify(result.detail || 'Voice service unavailable'));
  return result;
}
export class OrbVoice {
  private session = '';
  private stream?: MediaStream;
  private context?: AudioContext;
  private node?: ScriptProcessorNode;
  private timer?: number;
  private heartbeat?: number;
  private frames: Float32Array[] = [];
  private preRoll: Float32Array[] = [];
  private activity = new VoiceActivity();
  private audio?: HTMLAudioElement;
  private audioUrl?: string;
  private generation = 0;
  private request?: AbortController;
  private turnId = "";
  private inputRms = 0;
  private inputLabel = "";
  private captureId = "";
  private selectedInput = {device_id:"",label:"System default"};
  private preferencesLoaded = false;
  private rate = 48000;
  private handsFree = false;
  state = 'idle';
  constructor(private update:(state:string)=>void, private failure:(message:string)=>void) {}
  private report(extra:object = {}) {
    if (isTauri()) void invoke('voice_event',{event:{state:this.state,...extra}}).catch(()=>{});
  }
  private status(state:string) { this.state=state;this.update(state);this.report(); }
  async publishInputs() {
    const devices=await navigator.mediaDevices.enumerateDevices();
    const inputs=devices.filter(device=>device.kind==='audioinput').map(device=>({device_id:device.deviceId,label:device.label || 'Unnamed microphone'}));
    this.report({input_devices:inputs});return inputs;
  }
  async selectInput(value:{device_id:string,label:string}) {
    await this.suspend();this.selectedInput=value;this.preferencesLoaded=true;
    await this.startHandsFree();
  }
  async startHandsFree() {
    if (!this.preferencesLoaded && isTauri()) {
      const result=await invoke<{value:{device_id:string,label:string}}>('microphone_preferences');
      this.selectedInput=result.value;this.preferencesLoaded=true;
    }
    this.handsFree=true;
    if (this.state==='idle' || this.state==='blocked') await this.listen();
  }
  async toggle() {
    if (this.state==='listening' || this.state==='opening microphone') {await this.suspend();return;}
    if (this.state==='speaking' || this.state==='thinking') {await this.suspend();await this.startHandsFree();return;}
    await this.startHandsFree();
  }
  private async listen(monitorPlayback = false) {
    if (!this.handsFree) return;
    if (this.stream?.getAudioTracks().some(track=>track.readyState==='live')) {
      this.frames=[];this.preRoll=[];this.activity.reset();this.status('listening');return;
    }
    const generation=monitorPlayback ? this.generation : ++this.generation;
    if (!monitorPlayback) this.status('opening microphone');
    try {
      if (!navigator.mediaDevices?.getUserMedia) throw new Error('Microphone capture is unavailable in this webview.');
      const inputs=await this.publishInputs();
      let deviceId=this.selectedInput.device_id;
      if (this.selectedInput.label!=='System default') {
        const selected=inputs.find(device=>device.device_id===deviceId && device.label===this.selectedInput.label) || inputs.find(device=>device.label===this.selectedInput.label);
        if (!selected) throw new Error(`Selected microphone unavailable: ${this.selectedInput.label}. Connect it or select another input in Dock.`);
        deviceId=selected.device_id;
      }
      const stream=await navigator.mediaDevices.getUserMedia({audio:{...(deviceId ? {deviceId:{exact:deviceId}} : {}),echoCancellation:true,noiseSuppression:true,channelCount:1}});
      if (generation!==this.generation || (monitorPlayback && this.state!=='speaking')) {stream.getTracks().forEach(track=>track.stop());return;}
      this.stream=stream;this.captureId=crypto.randomUUID();
      this.inputLabel=stream.getAudioTracks()[0]?.label || "Default microphone";
      this.report({microphone:true,capture_id:this.captureId,input_label:this.inputLabel,error_message:"",error_name:""});
      this.session=await embodimentSession();
      if (generation!==this.generation || (monitorPlayback && this.state!=='speaking')) {this.release();return;}
      this.context=new AudioContext();
      await this.context.resume();
      this.rate=this.context.sampleRate;
      this.frames=[];this.preRoll=[];this.activity.reset();
      this.node=this.context.createScriptProcessor(4096,1,1);
      this.node.onaudioprocess=event=>{
        if (generation!==this.generation) return;
        const samples=new Float32Array(event.inputBuffer.getChannelData(0));
        this.inputRms=Math.sqrt(samples.reduce((sum,value)=>sum+value*value,0)/samples.length);
        if (!['listening','speaking'].includes(this.state)) return;
        const wasActive=this.activity.active;
        const activity=this.activity.observe(samples,this.rate);
        if (!wasActive) {
          this.preRoll.push(samples);
          if (this.preRoll.length>8) this.preRoll.shift();
          if (this.activity.active) {this.frames=this.preRoll;this.preRoll=[];}
        } else this.frames.push(samples);
        if (this.state==='speaking' && this.activity.active) {
          this.report({playback:'interrupted'});this.stopPlayback();this.status('listening');
        }
        if (activity==='complete') void this.finish();
      };
      this.context.createMediaStreamSource(stream).connect(this.node);
      this.node.connect(this.context.destination);
      if (!monitorPlayback) this.status('listening');
      this.report({microphone:true,sample_rate:this.rate,input_label:this.inputLabel});
      this.heartbeat=window.setInterval(()=>this.report({microphone:this.stream?.getTracks().some(track=>track.readyState==='live') || false,sample_rate:this.rate,input_rms:this.inputRms,capture_id:this.captureId}),2000);
    } catch(error) {
      this.release();this.handsFree=false;this.status('blocked');
      const name=error instanceof DOMException ? error.name : 'CaptureError';
      this.report({microphone:false,error_name:name,error_message:name==='NotAllowedError' ? 'Allow microphone access for Orbot, then retry listening.' : String(error).slice(0,500)});
      this.failure(name==='NotAllowedError' ? 'Microphone access was denied. Allow microphone access for Orbot, then click the Orb to retry.' : `Microphone: ${String(error)}`);
    }
  }
  private release() {
    clearTimeout(this.timer);clearInterval(this.heartbeat);this.heartbeat=undefined;this.node?.disconnect();this.node=undefined;
    this.stream?.getTracks().forEach(track=>track.stop());this.stream=undefined;
    void this.context?.close();this.context=undefined;
    this.report({microphone:false});
  }
  private resumeLater() {
    if (this.handsFree) this.timer=window.setTimeout(()=>{if(this.handsFree && this.state==='idle') void this.listen();},300);
  }
  private stopPlayback() {
    if (this.audio) {this.audio.onplaying=null;this.audio.onended=null;this.audio.onerror=null;this.audio.pause();}
    this.audio=undefined;
    if (this.audioUrl) URL.revokeObjectURL(this.audioUrl);
    this.audioUrl=undefined;
  }
  private async finish() {
    if(this.state!=='listening' || !this.activity.active) return;
    const generation=this.generation;
    this.status('thinking');
    try {
      const length=this.frames.reduce((sum,frame)=>sum+frame.length,0);
      this.report({capture_ms:Math.round(length*1000/this.rate)});
      const bytes=new Uint8Array(44+length*2);const view=new DataView(bytes.buffer);
      const text=(offset:number,value:string)=>[...value].forEach((char,i)=>view.setUint8(offset+i,char.charCodeAt(0)));
      text(0,'RIFF');view.setUint32(4,36+length*2,true);text(8,'WAVE');text(12,'fmt ');
      view.setUint32(16,16,true);view.setUint16(20,1,true);view.setUint16(22,1,true);
      view.setUint32(24,this.rate,true);view.setUint32(28,this.rate*2,true);view.setUint16(32,2,true);view.setUint16(34,16,true);
      text(36,'data');view.setUint32(40,length*2,true);let offset=44;
      for(const frame of this.frames) for(const sample of frame){view.setInt16(offset,Math.max(-1,Math.min(1,sample))*32767,true);offset+=2;}
      this.frames=[];this.preRoll=[];this.activity.reset();
      let encoded='';for(let i=0;i<bytes.length;i+=8192) encoded+=String.fromCharCode(...bytes.subarray(i,i+8192));
      this.request=new AbortController();this.turnId=crypto.randomUUID();
      const result=await post('/voice/input',{session_id:this.session,turn_id:this.turnId,audio_wav:btoa(encoded)},this.request.signal);
      this.turnId='';this.request=undefined;
      if(generation!==this.generation) return;
      if(typeof result.hearing?.text==='string') {
        const declined=/^\s*(no(?:[,.! ]|$)|not now\b|leave me\b|stop\b|quiet\b|later\b|i(?:'| a)m busy\b|don't\b|do not\b)/i.test(result.hearing.text);
        if(isTauri()) void invoke('attention_feedback',{declined}).catch(()=>{});
      }
      if(!result.audio_wav) throw new Error(result.speech_error || 'Qwen3-TTS returned no audio. Check Dock voice diagnostics.');
      const wav=Uint8Array.from(atob(result.audio_wav),char=>char.charCodeAt(0));
      this.audioUrl=URL.createObjectURL(new Blob([wav],{type:'audio/wav'}));
      this.audio=new Audio(this.audioUrl);
      this.audio.onplaying=()=>{if(generation!==this.generation)return;this.status('speaking');this.report({playback:'started',error_message:'',error_name:''});this.activity.reset();this.frames=[];this.preRoll=[];};
      this.audio.onended=()=>{this.report({playback:'ended',playback_seconds:this.audio?.currentTime || 0});this.stopPlayback();this.status('idle');this.resumeLater();};
      this.audio.onerror=()=>{this.report({playback:'failed',error_name:'AudioPlaybackError',error_message:'Speaker playback failed. Check the Windows output device and volume.'});this.release();this.stopPlayback();this.status('blocked');this.failure('Speaker playback failed.');};
      await this.audio.play();
    } catch(error) {
      if(generation===this.generation){this.turnId='';this.request=undefined;this.stopPlayback();this.status('idle');this.report({error_name:'VoicePipelineError',error_message:String(error).slice(0,500)});this.failure(String(error));this.resumeLater();}
    }
  }
  async playAttentionOffer(audioWav:string) {
    if(this.state!=='listening' || !this.handsFree) return;
    const generation=this.generation;
    this.frames=[];this.preRoll=[];this.activity.reset();this.stopPlayback();
    const wav=Uint8Array.from(atob(audioWav),char=>char.charCodeAt(0));
    this.audioUrl=URL.createObjectURL(new Blob([wav],{type:'audio/wav'}));
    this.audio=new Audio(this.audioUrl);
    this.audio.onplaying=()=>{if(generation!==this.generation)return;this.status('speaking');this.report({playback:'started',error_message:'',error_name:''});this.activity.reset();};
    this.audio.onended=()=>{if(generation!==this.generation)return;this.report({playback:'ended',playback_seconds:this.audio?.currentTime || 0});this.stopPlayback();this.status('idle');this.resumeLater();};
    this.audio.onerror=()=>{if(generation!==this.generation)return;this.report({playback:'failed',error_name:'AudioPlaybackError',error_message:'Speaker playback failed. Check the Windows output device and volume.'});this.stopPlayback();this.status('listening');};
    try {await this.audio.play();}
    catch(error) {if(generation===this.generation){this.stopPlayback();this.status('listening');this.failure(`Attention audio playback failed: ${String(error)}`);}}
  }
  async suspend() {
    this.handsFree=false;++this.generation;
    const turnId=this.turnId;this.turnId='';this.request?.abort();this.request=undefined;
    this.release();this.frames=[];this.preRoll=[];this.activity.reset();this.stopPlayback();this.status('idle');
    if(turnId && isTauri()) await invoke('cancel_voice',{sessionId:this.session,turnId});
  }
  async endSession() {
    await this.suspend();
    if(!this.session) this.session=await embodimentSession();
    if(this.session){const id=this.session;await post('/sessions/end',{session_id:id});this.session='';}
  }
}
