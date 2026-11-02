import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import ts from 'typescript';

function fixture(native = false) {
  const calls = [];
  const output = ts.transpileModule(fs.readFileSync(new URL('../src/voice.ts', import.meta.url), 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  const exports = {};
  const activityExports = {};
  const activitySource = ts.transpileModule(fs.readFileSync(new URL('../src/voice_activity.ts', import.meta.url), 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  vm.runInNewContext(activitySource, { exports: activityExports, module: { exports: activityExports } });
  const context = { exports, module: { exports }, clearTimeout, setTimeout, clearInterval,
    require: name => name === './voice_activity' ? activityExports : name === '@tauri-apps/api/core' ?
      { isTauri: () => native, invoke: async (name,args) => {calls.push({command:name,args});} } : { embodimentSession: async () => 'runtime-owned-fixture' },
    fetch: async (url, options) => { calls.push({ url, body: JSON.parse(options.body) }); return { ok: true, json: async () => ({ closed: true }) }; },
  };
  vm.runInNewContext(output, context);
  return { voice: new exports.OrbVoice(() => {}, () => {}), calls, Activity: activityExports.VoiceActivity };
}

test('explicit pause suspends media while preserving the active session', async () => {
  const { voice, calls } = fixture();
  voice.session = 'runtime-owned-fixture';
  voice.frames = [new Float32Array([0.1])];
  let paused = false;
  voice.audio = { pause: () => { paused = true; } };
  await voice.suspend();
  assert.equal(voice.session, 'runtime-owned-fixture');
  assert.equal(voice.frames.length, 0);
  assert.equal(paused, true);
  assert.equal(calls.length, 0);
});

test('only explicit session completion invokes the existing closing process', async () => {
  const { voice, calls } = fixture();
  voice.session = 'runtime-owned-fixture';
  await voice.endSession();
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url.endsWith('/sessions/end'), true);
  assert.equal(calls[0].body.session_id, 'runtime-owned-fixture');
  assert.equal(voice.session, '');
});

test('repeated explicit media pauses do not replace or close the session', async () => {
  const { voice, calls } = fixture();
  voice.session = 'runtime-owned-fixture';
  await voice.suspend(); await voice.suspend(); await voice.suspend();
  assert.equal(voice.session, 'runtime-owned-fixture');
  assert.equal(calls.length, 0);
});

test('silence does not produce a spoken turn', () => {
  const { Activity } = fixture(); const detector = new Activity();
  for (let i=0;i<500;i++) assert.equal(detector.observe(new Float32Array(4800),48000),'waiting');
  assert.equal(detector.active,false);
});

test('a spoken turn is submitted after the end-of-speech pause', () => {
  const { Activity } = fixture(); const detector = new Activity();
  const speech = new Float32Array(4800).fill(0.08), silence = new Float32Array(4800);
  detector.observe(speech,48000);assert.equal(detector.observe(speech,48000),'speech');
  for(let i=0;i<7;i++) assert.notEqual(detector.observe(silence,48000),'complete');
  assert.equal(detector.observe(silence,48000),'complete');
});

test('short incidental noise does not count as a spoken turn', () => {
  const { Activity } = fixture(); const detector = new Activity();
  detector.observe(new Float32Array(4800).fill(0.08),48000);
  detector.observe(new Float32Array(4800),48000);
  assert.equal(detector.active,false);
});

test('continuous capture has a bounded utterance duration', () => {
  const { Activity } = fixture(); const detector = new Activity();
  let state; for(let i=0;i<160;i++) state=detector.observe(new Float32Array(4800).fill(0.08),48000);
  assert.equal(state,'complete');
});


test('explicit cancellation aborts the pending request and requests cancellation without ending the session', async () => {
  const {voice,calls}=fixture(true);
  voice.session='runtime-owned-fixture';voice.turnId='active-turn';
  let aborted=false;voice.request={abort:()=>{aborted=true;}};
  await voice.suspend();
  assert.equal(aborted,true);
  assert.equal(voice.session,'runtime-owned-fixture');
  assert.equal(calls.filter(call=>call.command==='cancel_voice').length,1);
  assert.equal(calls.find(call=>call.command==='cancel_voice').args.turnId,'active-turn');
  assert.equal(calls.some(call=>call.url?.endsWith('/sessions/end')),false);
});

test('automatic launch starts listening without a manual toggle', async () => {
  const {voice}=fixture();let opened=0;
  voice.listen=async()=>{opened++;voice.state='listening';};
  await voice.startHandsFree();
  assert.equal(opened,1);assert.equal(voice.state,'listening');
});


test('rearming a turn reuses the live microphone stream', async () => {
  const {voice}=fixture();const stream={getAudioTracks:()=>[{readyState:'live'}]};
  voice.stream=stream;voice.generation=7;voice.preferencesLoaded=true;
  await voice.startHandsFree();
  assert.equal(voice.stream,stream);assert.equal(voice.generation,7);assert.equal(voice.state,'listening');
});
