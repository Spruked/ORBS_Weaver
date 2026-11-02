import * as THREE from "three";

export type OrbShape = "sphere" | "liquid" | "hexagon";
export type OrbVisualState = "idle" | "listening" | "thinking" | "speaking";

const VERTEX = `varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`;
const FRAGMENT = `
uniform sampler2D uImage; uniform float uIntensity; uniform float uPulse; uniform float uTime; varying vec2 vUv;
mat2 rotate2d(float a){float s=sin(a),c=cos(a);return mat2(c,-s,s,c);}
void main(){vec2 p=vUv-vec2(.5);float r=length(p);float mask=1.0-smoothstep(.19+.035*uPulse,.235+.035*uPulse,r);
if(mask<=0.0||uIntensity<=0.0)discard;float well=1.0-smoothstep(0.0,.22,r);vec2 swelled=p*(1.0-.26*uPulse*well);
float twist=(2.2*sin(uTime*2.3)+1.1*sin(uTime*.9+1.3))*well;vec3 painted=texture2D(uImage,rotate2d(twist)*swelled+vec2(.5)).rgb;
float theta=atan(p.y,p.x);float arms=.5+.5*sin(3.0*theta+24.0*r-uTime*5.0);arms*=smoothstep(.01,.05,r)*(1.0-smoothstep(.15,.21,r));
vec3 swirl=mix(vec3(.10,.52,1.0),vec3(.92,.98,1.0),smoothstep(.3,.85,arms))*arms;float level=mix(.6,1.5,uPulse);
vec3 color=painted*level+swirl*(.25+.65*uPulse)+vec3(.30,.72,1.0)*pow(well,1.6)*uPulse*.8;gl_FragColor=vec4(color,mask*uIntensity);
#include <colorspace_fragment>}`;

function contour(shape: OrbShape, angle: number, swell = 0): number {
  if (shape === "hexagon") {
    const sector = Math.PI / 3;
    const offset = ((angle + Math.PI / 6) % sector + sector) % sector - Math.PI / 6;
    return Math.cos(Math.PI / 6) / Math.cos(offset);
  }
  if (shape === "liquid") return 1 + .09 * Math.sin(3 * angle + swell) + .035 * Math.sin(5 * angle - swell * .7);
  return 1;
}

function makeDisc(shape: OrbShape, front: boolean, swell: number): THREE.BufferGeometry {
  const segments = 144, rings = 26, depth = .32;
  const positions: number[] = [], uvs: number[] = [], indices: number[] = [];
  for (let ring = 0; ring <= rings; ring++) {
    const radius = ring / rings;
    for (let segment = 0; segment <= segments; segment++) {
      const a = segment / segments * Math.PI * 2;
      const boundary = contour(shape, a, swell);
      const x = radius * boundary * Math.cos(a), y = radius * boundary * Math.sin(a);
      const z = (front ? 1 : -1) * depth * Math.sqrt(Math.max(0, 1 - radius * radius));
      positions.push(x, y, z); uvs.push((x + 1) / 2, (y + 1) / 2);
    }
  }
  for (let ring = 0; ring < rings; ring++) for (let segment = 0; segment < segments; segment++) {
    const a = ring * (segments + 1) + segment, b = a + 1, c = a + segments + 1, d = c + 1;
    if (front) indices.push(a, c, d, a, d, b); else indices.push(a, d, c, a, b, d);
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute("uv", new THREE.Float32BufferAttribute(uvs, 2));
  geometry.setIndex(indices); geometry.computeVertexNormals(); return geometry;
}

export class Orb3D {
  private renderer: THREE.WebGLRenderer;
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private orb = new THREE.Group();
  private eye: THREE.Mesh;
  private eyeMaterial: THREE.ShaderMaterial;
  private texture: THREE.Texture;
  private parts: THREE.Object3D[] = [];
  private geometries: THREE.BufferGeometry[] = [];
  private shape: OrbShape = "sphere";
  private state: OrbVisualState = "idle";
  private gaze = { x: 0, y: 0 };
  private look = { x: 0, y: 0 };
  private seconds = 0;
  private speech = 0;
  private frame = 0;
  private observer: ResizeObserver;
  private disposed = false;

  private constructor(private host: HTMLElement, texture: THREE.Texture) {
    this.texture = texture;
    this.renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: "high-performance" });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
    this.renderer.setClearColor(0, 0); this.renderer.toneMapping = THREE.ACESFilmicToneMapping; this.renderer.toneMappingExposure = 1.1;
    this.renderer.domElement.className = "orb-canvas"; host.appendChild(this.renderer.domElement);
    this.scene = new THREE.Scene(); this.camera = new THREE.PerspectiveCamera(30, 1, .1, 20); this.camera.position.z = 4.35;
    this.scene.add(new THREE.AmbientLight(0xffffff, 1.5));
    const edge = new THREE.DirectionalLight(0x83cfff, 2.2); edge.position.set(-2, 2, 4); this.scene.add(edge);
    this.scene.add(this.orb);
    const faceMaterial = new THREE.MeshBasicMaterial({ map: texture, side: THREE.DoubleSide, toneMapped: false });
    const backMaterial = new THREE.MeshPhysicalMaterial({ color: 0x870e0c, metalness: .48, roughness: .27, clearcoat: 1, clearcoatRoughness: .12, side: THREE.DoubleSide });
    const rimMaterial = new THREE.MeshStandardMaterial({ color: 0x500806, metalness: .72, roughness: .26 });
    const faceGeo = makeDisc("sphere", true, 0), backGeo = makeDisc("sphere", false, 0), eyeGeo = faceGeo.clone(); eyeGeo.translate(0, 0, .004);
    this.geometries.push(faceGeo, backGeo, eyeGeo);
    this.eyeMaterial = new THREE.ShaderMaterial({ vertexShader: VERTEX, fragmentShader: FRAGMENT,
      uniforms: { uImage: { value: texture }, uIntensity: { value: 0 }, uPulse: { value: 0 }, uTime: { value: 0 } }, transparent: true, depthWrite: false });
    this.eye = new THREE.Mesh(eyeGeo, this.eyeMaterial); this.eye.visible = false;
    this.parts = [new THREE.Mesh(faceGeo, faceMaterial), this.eye, new THREE.Mesh(backGeo, backMaterial),
      new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(Array.from({length:145},(_,i)=>{const a=i/144*Math.PI*2;return new THREE.Vector3(Math.cos(a),Math.sin(a),0);})),144,.014,10,true),rimMaterial)];
    this.parts.forEach(part => this.orb.add(part));
    this.observer = new ResizeObserver(() => this.resize()); this.observer.observe(host); this.resize(); this.animate();
  }

  static async create(host: HTMLElement): Promise<Orb3D> {
    const loader = new THREE.TextureLoader();
    const texture = await loader.loadAsync("/orb/redorbbluecenter1600.png");
    texture.colorSpace = THREE.SRGBColorSpace;
    texture.anisotropy = 4;
    return new Orb3D(host, texture);
  }
  setState(state: OrbVisualState) { this.state = state; }
  setGaze(x: number, y: number) { this.gaze = { x: Math.max(-1,Math.min(1,x)), y: Math.max(-1,Math.min(1,y)) }; }
  setShape(shape: OrbShape) { if (shape !== this.shape) { this.shape = shape; this.rebuildShape(); } }
  private rebuildShape() {
    const old = this.parts.slice(0,3);
    old.forEach(part => { this.orb.remove(part); const mesh=part as THREE.Mesh; mesh.geometry?.dispose(); if(part!==this.eye)(mesh.material as THREE.Material)?.dispose(); });
    const faceGeo=makeDisc(this.shape,true,this.seconds), backGeo=makeDisc(this.shape,false,this.seconds), eyeGeo=faceGeo.clone(); eyeGeo.translate(0,0,.004);
    this.geometries.push(faceGeo,backGeo,eyeGeo);
    const faceMaterial = new THREE.MeshBasicMaterial({map:this.texture,side:THREE.DoubleSide,toneMapped:false});
    const backMaterial = new THREE.MeshPhysicalMaterial({color:0x870e0c,metalness:.48,roughness:.27,clearcoat:1,clearcoatRoughness:.12,side:THREE.DoubleSide});
    this.eye.geometry.dispose(); this.eye.geometry=eyeGeo;
    const updated:THREE.Object3D[]=[new THREE.Mesh(faceGeo,faceMaterial),this.eye,new THREE.Mesh(backGeo,backMaterial)];
    updated.forEach(part=>this.orb.add(part)); this.parts=updated.concat(this.parts.slice(3));
    const rim=this.parts[3] as THREE.Mesh; rim.geometry.dispose();
    const points=Array.from({length:145},(_,i)=>{const a=i/144*Math.PI*2,r=contour(this.shape,a,this.seconds);return new THREE.Vector3(r*Math.cos(a),r*Math.sin(a),0);});
    rim.geometry=new THREE.TubeGeometry(new THREE.CatmullRomCurve3(points),144,.014,10,true);
  }
  private resize() { const w=Math.max(1,this.host.clientWidth),h=Math.max(1,this.host.clientHeight); this.camera.aspect=w/h; this.camera.updateProjectionMatrix(); this.renderer.setSize(w,h,false); }
  private animate = () => {
    if (this.disposed) return;
    this.frame=requestAnimationFrame(this.animate);
    const dt=Math.min(.1,this.clock()); this.seconds+=dt;
    const setting={idle:{angle:.16,speed:.55,pulse:0},listening:{angle:.19,speed:.75,pulse:.012},thinking:{angle:.23,speed:1.05,pulse:.008},speaking:{angle:.17,speed:.85,pulse:0}}[this.state];
    const ease=1-Math.exp(-dt/.16); this.look.x+=(this.gaze.x-this.look.x)*ease; this.look.y+=(this.gaze.y-this.look.y)*ease;
    const attention=Math.min(1,Math.hypot(this.look.x,this.look.y));
    this.orb.rotation.y=Math.sin(this.seconds*setting.speed)*setting.angle*(1-.85*attention)+this.look.x*.5;
    this.orb.rotation.x=this.look.y*.34;
    this.orb.scale.setScalar(1+Math.sin(this.seconds*5.5)*setting.pulse);
    const speaking=this.state==="speaking"; this.speech+=(Number(speaking)-this.speech)*(1-Math.exp(-dt/(speaking ? .18 : .4)));
    this.eye.visible=this.speech>.003; const beat=Math.pow(.5+.5*Math.sin(this.seconds*10),1.3)*(.8+.2*Math.sin(this.seconds*3.3));
    this.eyeMaterial.uniforms.uIntensity.value=this.speech; this.eyeMaterial.uniforms.uPulse.value=beat; this.eyeMaterial.uniforms.uTime.value=this.seconds;
    this.renderer.render(this.scene,this.camera);
  };
  private lastTime=performance.now();
  private clock() { const now=performance.now(),dt=(now-this.lastTime)/1000;this.lastTime=now;return dt; }
  dispose() {
    this.disposed=true; cancelAnimationFrame(this.frame); this.observer.disconnect(); this.parts.forEach(p=>{const m=p as THREE.Mesh;m.geometry?.dispose();(m.material as THREE.Material)?.dispose();});
    this.geometries.forEach(g=>g.dispose()); this.eyeMaterial.dispose(); this.texture.dispose(); this.renderer.dispose(); this.renderer.domElement.remove();
  }
}
