// classic script — THREE from vendored UMD build (file:// safe)
// s02 顶视爆炸剖面 — 真 3D 电芯模组,由 hf-seek 全局时间驱动(s02 窗口 7.0–13.18s)
const S0 = 7.0, DUR = 6.18, HOT = 5, COLS = 11;
const canvas = document.getElementById("s02canvas");
const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, preserveDrawingBuffer: true });
renderer.setSize(1920, 1080, false); renderer.setPixelRatio(1);
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;

const scene = new THREE.Scene(); scene.fog = new THREE.Fog(0x0c0f14, 26, 62);
const cam = new THREE.PerspectiveCamera(36, 1920 / 1080, 0.1, 100);
scene.add(new THREE.AmbientLight(0x3d9df6, 0.15));
const key = new THREE.DirectionalLight(0xdfe8ff, 0.5); key.position.set(6, 14, 8); scene.add(key);
const rim = new THREE.DirectionalLight(0x3d9df6, 0.42); rim.position.set(-8, 5, -7); scene.add(rim);

const H0 = new THREE.Color(0xffb02e), H1 = new THREE.Color(0xff5a1f), H2 = new THREE.Color(0xfff3e0);
const cw = 1.5, cd = 3.0, ch = 2.8, gx = 0.24, totalW = COLS * cw + (COLS - 1) * gx;
const boxGeo = new THREE.BoxGeometry(cw, ch, cd), edgeGeo = new THREE.EdgesGeometry(boxGeo);
const postGeo = new THREE.CylinderGeometry(0.14, 0.14, 0.3, 14);
function glowTex() {
  const c = document.createElement("canvas"); c.width = c.height = 128; const x = c.getContext("2d");
  const g = x.createRadialGradient(64, 64, 0, 64, 64, 64);
  g.addColorStop(0, "rgba(255,243,224,1)"); g.addColorStop(.4, "rgba(255,120,30,.6)"); g.addColorStop(1, "rgba(255,90,30,0)");
  x.fillStyle = g; x.fillRect(0, 0, 128, 128); return new THREE.CanvasTexture(c);
}

// env reflection: tiny equirect gradient -> PMREM (instant material richness on metal)
(function(){
  const c=document.createElement("canvas");c.width=64;c.height=32;const x=c.getContext("2d");
  const g=x.createLinearGradient(0,0,0,32);
  g.addColorStop(0,"#2a3550");g.addColorStop(.45,"#0e1420");g.addColorStop(.55,"#33210f");g.addColorStop(1,"#050608");
  x.fillStyle=g;x.fillRect(0,0,64,32);
  x.fillStyle="rgba(190,215,255,.9)";x.fillRect(6,2,10,5); // cool softbox
  x.fillStyle="rgba(255,140,50,.8)";x.fillRect(40,12,14,6); // warm bounce
  const tex=new THREE.CanvasTexture(c);tex.mapping=THREE.EquirectangularReflectionMapping;
  const pm=new THREE.PMREMGenerator(renderer);scene.environment=pm.fromEquirectangular(tex).texture;
})();

const cells = [];
for (let i = 0; i < COLS; i++) {
  const grp = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color: 0x171a20, metalness: .75, roughness: .3, emissive: 0x000000 });
  grp.add(new THREE.Mesh(boxGeo, mat));
  grp.add(new THREE.LineSegments(edgeGeo, new THREE.LineBasicMaterial({ color: 0xe8e6e1, transparent: true, opacity: .8 })));
  const pmat = new THREE.MeshStandardMaterial({ color: 0xc9ccd2, metalness: .9, roughness: .3 });
  for (const sx of [-.5, .5]) { const p = new THREE.Mesh(postGeo, pmat); p.position.set(sx * cw * .5, ch / 2 + .12, cd * .3); grp.add(p); }
  grp.position.set(i * (cw + gx) - totalW / 2 + cw / 2, 0, 0);
  scene.add(grp);
  const cell = { grp, mat, base: 0, glow: null };
  if (i === HOT) {
    const gl = new THREE.Sprite(new THREE.SpriteMaterial({ map: glowTex(), color: 0xff7a1f, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
    gl.scale.set(7.5, 7.5, 1); grp.add(gl); cell.glow = gl;
  }
  cells.push(cell);
}
const tray = new THREE.Mesh(new THREE.BoxGeometry(totalW + 1, .5, cd + 1),
  new THREE.MeshStandardMaterial({ color: 0x0f1217, metalness: .7, roughness: .5 }));
tray.position.y = -ch / 2 - .3; scene.add(tray);

const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const sm = (e0, e1, x) => { const t = clamp((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t); };
const sp = new THREE.Vector3(10, 7.5, 14.5), ep = new THREE.Vector3(2.6, 3.4, 8.2);
function renderAt(time) {
  const lt = clamp(time, 0, DUR), p = lt / DUR;
  const heat = sm(.18, .55, p);
  const hc = cells[HOT];
  hc.mat.color.copy(new THREE.Color(0x171a20).lerp(H1, heat * .85));
  hc.mat.emissive.copy(H0.clone().lerp(H2, heat)); hc.mat.emissiveIntensity = 0.35 + heat * heat * 1.35;
  if (hc.glow) { hc.glow.material.opacity = .2 + .8 * heat; hc.glow.scale.setScalar(5 + 3 * heat); }
  for (let d = 1; d <= 2; d++) { const w = Math.max(0, heat - d * .38);
    for (const j of [HOT - d, HOT + d]) if (cells[j]) { cells[j].mat.emissive.copy(H0); cells[j].mat.emissiveIntensity = w * w * 0.55; } }
  const ex = sm(.62, 1, p) * 1.3;
  cells[HOT].grp.position.y = ex;
  cam.position.lerpVectors(sp, ep, sm(0, 1, p)); cam.lookAt(0, -.2 + ex * .5, 0);
  renderer.render(scene, cam);
}
// primary driver: GSAP timeline onUpdate (HyperFrames always seeks the gsap timeline) passes LOCAL time
window.__renderS02 = renderAt;
// fallback: three adapter hf-seek (global time)
window.addEventListener("hf-seek", (e) => renderAt(e.detail.time - S0));
renderAt(0);
