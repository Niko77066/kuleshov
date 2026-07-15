#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the HyperFrames composition (compose/final.html) for 800V thermal runaway.
Data-driven from the audio-locked timeline. Seedance clips mounted with tail-trim to their slots;
MG shots authored as engineering-anatomy styled cards; s03 Ken Burns; data overlays; grade layer.
"""
import os
OUT = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, TOTAL = 1920, 1080, 24, 90.43
_ff = f"{OUT}/assets/fonts/faces.css"
FONT_FACES = open(_ff).read() if os.path.exists(_ff) else ""

# (id, start, end, kind, payload)  — kinds: seedance | kenburns | mg  (mg payload = builder key)
SHOTS = [
 ("s01", 0.00,  7.00, "seedance", "s01.mp4"),
 ("s02", 7.00, 13.18, "seedance", "s02.mp4"),
 ("s03",13.18, 18.60, "kenburns","s03_microlayers.png"),
 ("s04",18.60, 25.94, "seedance","s04.mp4"),
 ("s05",25.94, 33.20, "seedance","s05.mp4"),
 ("s06",33.20, 37.40, "mg", "temp743"),
 ("s07",37.40, 41.58, "mg", "oxygen"),
 ("s08",41.58, 48.20, "seedance","s08.mp4"),
 ("s09",48.20, 52.20, "mg", "paths"),
 ("s10",52.20, 54.82, "mg", "progress"),
 ("s11",54.82, 60.20, "seedance","s11.mp4"),
 ("s12",60.20, 68.74, "seedance","s12.mp4"),
 ("s13",68.74, 74.20, "mg", "protect"),
 ("s14",74.20, 78.80, "mg", "progress_cut"),
 ("s15",78.80, 85.40, "seedance","s15.mp4"),
 ("s16",85.40, 90.43, "mg", "closing"),
]
WHITE_FLASH = ["s04", "s11"]  # entry white flash (点火瞬间)

# ---------- element builders (return inner HTML for the shot's track-1 div) ----------
def mg_cutaway():  # s02 顶视爆炸剖面(SVG 电芯阵列,一颗点热色)
    cells = ""
    for i in range(11):
        hot = i == 5
        fill = "url(#hot)" if hot else "#171a20"
        stroke = "#FF5A1F" if hot else "#2A2F38"
        cells += f'<rect x="{60+i*160}" y="300" width="120" height="440" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    return f'''<svg viewBox="0 0 1920 1080" class="fill">
      <defs><linearGradient id="hot" x1="0" y1="1" x2="0" y2="0">
        <stop offset="0" stop-color="#FFF3E0"/><stop offset=".5" stop-color="#FF5A1F"/><stop offset="1" stop-color="#FFB02E"/></linearGradient></defs>
      <rect x="30" y="270" width="1810" height="500" rx="18" fill="none" stroke="#2A2F38" stroke-width="3"/>
      {cells}
      <g class="anno" opacity="0">
        <line x1="900" y1="300" x2="900" y2="180" stroke="#E8E6E1" stroke-width="1.5"/><rect x="895" y="172" width="10" height="10" fill="#E8E6E1"/>
        <text x="920" y="185" fill="#E8E6E1" font-family="'Noto Sans SC',sans-serif" font-size="30" font-weight="700">一颗电芯失控</text>
      </g>
    </svg>'''

def mg_temp743():  # s06 温度大数字 + 对比锚
    return '''<div class="card">
      <div class="bignum"><span class="cnt" data-to="743">0</span><span class="unit">°C</span></div>
      <div class="anchor-bar">足以熔化铝 &nbsp;·&nbsp; 铝熔点 <b>660°C</b></div>
    </div>'''

def mg_oxygen():  # s07 正极释氧
    return '''<div class="card">
      <svg viewBox="0 0 600 600" class="o2">
        <circle cx="300" cy="300" r="150" fill="none" stroke="#FF5A1F" stroke-width="3"/>
        <g fill="#FFB02E" font-family="'JetBrains Mono',monospace" font-size="40" font-weight="700">
          <text x="120" y="180" class="o2a" opacity="0">O₂</text><text x="440" y="220" class="o2a" opacity="0">O₂</text>
          <text x="150" y="450" class="o2a" opacity="0">O₂</text><text x="430" y="440" class="o2a" opacity="0">O₂</text></g>
      </svg>
      <div class="label">正极高温释氧 — 自带助燃剂</div>
    </div>'''

def mg_paths():  # s09 四条传热路径
    items = ["芯壁传导","金属汇流排","高温喷气","热辐射"]
    rows = "".join(f'<div class="path" style="--i:{i}"><span class="dot"></span>{t}</div>' for i,t in enumerate(items))
    return f'<div class="card"><div class="paths-title">热量奔向邻芯的四条路</div><div class="paths">{rows}</div></div>'

def _progress(cut=False):  # s10 / s14 链路进度条
    nodes = ["电芯","邻芯","模组","整包"]
    active = 1 if cut else 2
    seg=""
    for i,n in enumerate(nodes):
        cls = "node hot" if i<=active and not (cut and i>1) else "node"
        if cut and i==1: cls="node hot stop"
        seg += f'<div class="{cls}"><span></span><em>{n}</em></div>'
        if i<len(nodes)-1: seg += f'<div class="link {"lit" if i<active and not cut else ""}"></div>'
    cap = "拦在邻芯 — 拆掉多米诺" if cut else "大约每 50 秒沦陷一颗"
    return f'<div class="card"><div class="chain">{seg}</div><div class="chain-cap">{cap}</div></div>'
def mg_progress(): return _progress(False)
def mg_progress_cut(): return _progress(True)

def mg_protect():  # s13 防护件逐层装入
    items=["电芯间 · 气凝胶隔热垫","模组间 · 云母板","定向排气道 · 引开高温烟气"]
    rows="".join(f'<div class="layer" style="--i:{i}"><span class="chk"></span>{t}</div>' for i,t in enumerate(items))
    return f'<div class="card"><div class="protect-title">工程师的答案:拆掉多米诺</div><div class="layers">{rows}</div></div>'

def mg_closing():  # s16 收尾卡
    return '''<div class="card closing">
      <div class="verdict"><span class="cnt" data-to="2">0</span><span class="unit">小时</span></div>
      <div class="verdict-sub">整包不起火 · 不爆炸</div>
      <div class="verdict-src">GB 38031-2025 · 2026.07.01 生效</div>
    </div>'''

MG = {"cutaway":mg_cutaway,"temp743":mg_temp743,"oxygen":mg_oxygen,"paths":mg_paths,
      "progress":mg_progress,"progress_cut":mg_progress_cut,"protect":mg_protect,"closing":mg_closing}

# data overlays (id, shot, html, pos-class)
S02_ANNO = ('<svg id="ov_s02anno" class="anno3d" viewBox="0 0 1920 1080"><g opacity="0">'
 '<line x1="1060" y1="430" x2="1060" y2="230" stroke="#E8E6E1" stroke-width="1.5"/>'
 '<rect x="1054" y="222" width="12" height="12" fill="#E8E6E1"/>'
 '<text x="1085" y="240" fill="#E8E6E1" font-family="\'Noto Sans SC\',sans-serif" font-size="34" font-weight="700">一颗电芯失控</text></g></svg>')
OVERLAYS = [
 ("s01", '<div class="ov anchor-card"><div class="ov-date">2026.07.01</div><div class="ov-std">GB 38031-2025</div><div class="ov-hl">不起火 · 不爆炸</div></div>'),
 ("s02", S02_ANNO),
 ("s04", '<div class="ov temp-chip"><span class="cnt" data-to="130">90</span>°C · 隔膜熔穿</div>'),
 ("s12", '<div class="ov water-bar">灭火需上万升水 · 48 小时内仍可能复燃</div>'),
 ("s15", '<div class="ov twoh">整包 <b>2 小时</b> 不起火不爆炸</div>'),
 ("s16", '<div class="ov footer">信息截至 2026-07</div>'),
]

def esc(s): return s

# ---------- build tracks ----------
def clip_div(sid, s, e, kind, payload):
    dur = round(e - s, 3)
    if kind == "seedance":
        return (f'<video id="{sid}" class="clip shot" data-start="{s}" data-duration="{dur}" '
                f'data-track-index="1" src="assets/clips/{payload}" muted playsinline></video>')
    if kind == "kenburns":
        return (f'<div id="{sid}" class="clip shot kb" data-start="{s}" data-duration="{dur}" data-track-index="1">'
                f'<img src="assets/img/{payload}" class="fill"/></div>')
    if kind == "webgl3d":
        return (f'<div id="{sid}" class="clip shot mg3d" data-start="{s}" data-duration="{dur}" data-track-index="1">'
                f'<canvas id="s02canvas" class="fill"></canvas>'
                f'<svg class="anno3d" viewBox="0 0 1920 1080"><g opacity="0">'
                f'<line x1="960" y1="470" x2="960" y2="250" stroke="#E8E6E1" stroke-width="1.5"/><rect x="954" y="242" width="12" height="12" fill="#E8E6E1"/>'
                f'<text x="985" y="258" fill="#E8E6E1" font-family="\'Noto Sans SC\',sans-serif" font-size="34" font-weight="700">一颗电芯失控</text></g></svg></div>')
    # mg
    return (f'<div id="{sid}" class="clip shot mg" data-start="{s}" data-duration="{dur}" data-track-index="1">'
            f'{MG[payload]()}</div>')

shots_html = "\n      ".join(clip_div(*sh) for sh in SHOTS)
_span = {sh[0]: (sh[1], sh[2]) for sh in SHOTS}
ov_html = "\n      ".join(
    (lambda s,e: f'<div id="ov_{sid}" class="clip ov-wrap" data-start="{s}" data-duration="{round(e-s,3)}" data-track-index="2">{html}</div>')(*_span[sid])
    for sid, html in OVERLAYS)

# gsap timeline: hard-cut show/hide per shot window + intra-shot anims + flash + counters
tl_lines = []
for sid,s,e,kind,payload in SHOTS:
    tl_lines.append(f"tl.set('#{sid}',{{opacity:0}},0);")
for sid,s,e,kind,payload in SHOTS:
    # crossfade-free hard cut: opacity 1 at start, 0 at end (instant)
    tl_lines.append(f"tl.set('#{sid}',{{opacity:1}},{s});")
    tl_lines.append(f"tl.set('#{sid}',{{opacity:0}},{round(e,3)});")
    if kind=="kenburns":
        tl_lines.append(f"tl.fromTo('#{sid} img',{{scale:1.0}},{{scale:1.14,duration:{round(e-s,3)},ease:'none'}},{s});")
    if sid=="s02":
        tl_lines.append(f"tl.to('#ov_s02anno g',{{opacity:1,duration:0.5}},{round(s+2.6,3)});")
    if sid=="s07":
        tl_lines.append(f"tl.to('#s07 .o2a',{{opacity:1,stagger:0.18,duration:0.3}},{round(s+0.6,3)});")
# white flash overlay at ignition shots
for sid in WHITE_FLASH:
    st=[x for x in SHOTS if x[0]==sid][0][1]
    tl_lines.append(f"tl.set('#flash',{{opacity:0.9}},{round(st-0.06,3)});")
    tl_lines.append(f"tl.to('#flash',{{opacity:0,duration:0.18,ease:'power1.out'}},{round(st-0.02,3)});")
# overlays timing
for sid,html in OVERLAYS:
    sh=[x for x in SHOTS if x[0]==sid][0]
    s,e=sh[1],sh[2]
    tl_lines.append(f"tl.set('#ov_{sid}',{{opacity:0}},0);")
    tl_lines.append(f"tl.to('#ov_{sid}',{{opacity:1,duration:0.4}},{round(s+0.3,3)});")
    tl_lines.append(f"tl.to('#ov_{sid}',{{opacity:0,duration:0.3}},{round(e-0.4,3)});")
# count-ups
tl_lines.append("""document.querySelectorAll('.cnt').forEach(el=>{const to=+el.dataset.to,from=+el.textContent;const o={v:from};const host=el.closest('.clip,.ov-wrap');const st=host?+host.dataset.start:0;tl.to(o,{v:to,duration:0.6,ease:'power2.out',onUpdate:()=>{el.textContent=Math.round(o.v);}},st+0.2);});""")
# black end 0.3s
tl_lines.append(f"tl.to('#blackout',{{opacity:1,duration:0.3}},{round(TOTAL-0.3,3)});")
tl_lines.append(f"tl.set('#blackout',{{opacity:1}},{round(TOTAL-0.001,3)});")
timeline_js = "\n        ".join(tl_lines)

HTML = f'''<!doctype html>
<html lang="zh">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width={W}, height={H}"/>
<script src="assets/vendor/gsap.min.js"></script>
<style>
{FONT_FACES}
  *{{margin:0;padding:0;box-sizing:border-box;}}
  html,body{{width:{W}px;height:{H}px;overflow:hidden;background:#0C0F14;}}
  #root{{width:{W}px;height:{H}px;background:#0C0F14;position:relative;overflow:hidden;
    font-family:'Noto Sans SC',system-ui,sans-serif;color:#E8E6E1;}}
  #root>*{{position:absolute;inset:0;}}
  .shot{{width:{W}px;height:{H}px;object-fit:cover;}}
  .fill{{width:100%;height:100%;object-fit:cover;}}
  .kb img{{transform-origin:60% 55%;animation:none;}}
  /* MG cards */
  .mg{{display:flex;align-items:center;justify-content:center;background:#0C0F14;}}
  .mg3d{{background:#0C0F14;}} #s02canvas{{width:100%;height:100%;display:block;}}
  .anno3d{{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;}}
  .card{{width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:36px;}}
  .bignum,.verdict{{font-family:'JetBrains Mono',monospace;font-weight:800;font-size:300px;line-height:1;
    color:#FFF3E0;letter-spacing:-4px;display:flex;align-items:baseline;gap:14px;
    text-shadow:0 0 60px rgba(255,90,31,.55);}}
  .bignum .unit,.verdict .unit{{font-size:120px;color:#FF5A1F;}}
  .anchor-bar,.verdict-sub{{font-size:40px;color:#E8E6E1;letter-spacing:2px;}}
  .anchor-bar b{{color:#3D9DF6;}}
  .verdict-sub{{color:#FFB02E;font-weight:700;}}
  .verdict-src{{font-size:26px;color:#8a8f98;letter-spacing:1px;font-family:'JetBrains Mono',monospace;}}
  .label,.paths-title,.protect-title,.chain-cap{{font-size:40px;font-weight:700;letter-spacing:2px;}}
  .paths{{display:flex;flex-direction:column;gap:22px;}}
  .path{{display:flex;align-items:center;gap:20px;font-size:44px;color:#E8E6E1;}}
  .path .dot{{width:22px;height:22px;border-radius:3px;background:linear-gradient(#FFB02E,#FF5A1F);box-shadow:0 0 18px #FF5A1F;}}
  .chain{{display:flex;align-items:center;gap:0;}}
  .node{{display:flex;flex-direction:column;align-items:center;gap:12px;}}
  .node span{{width:46px;height:46px;border-radius:8px;background:#171a20;border:2px solid #2A2F38;}}
  .node.hot span{{background:linear-gradient(#FFB02E,#FF5A1F);border-color:#FF5A1F;box-shadow:0 0 26px #FF5A1F;}}
  .node.stop span{{box-shadow:0 0 26px #3D9DF6;border-color:#3D9DF6;}}
  .node em{{font-style:normal;font-size:30px;color:#cfccc4;}}
  .link{{width:120px;height:4px;background:#2A2F38;margin:0 6px 34px;}}
  .link.lit{{background:linear-gradient(90deg,#FFB02E,#FF5A1F);}}
  .layers,.paths{{margin-top:8px;}}
  .layer{{display:flex;align-items:center;gap:20px;font-size:42px;margin:16px 0;color:#E8E6E1;}}
  .layer .chk{{width:26px;height:26px;border-radius:50%;border:3px solid #3D9DF6;box-shadow:0 0 16px #3D9DF6;}}
  .o2{{width:520px;height:520px;}}
  /* overlays */
  .ov-wrap{{position:absolute;inset:0;pointer-events:none;}}
  .ov{{position:absolute;font-weight:700;}}
  .anchor-card{{left:110px;top:120px;border-left:6px solid #C8451B;padding:18px 30px;background:rgba(12,15,20,.35);}}
  .anchor-card .ov-date{{font-family:'JetBrains Mono',monospace;font-size:70px;color:#FFF3E0;}}
  .anchor-card .ov-std{{font-size:32px;color:#8a8f98;letter-spacing:2px;}}
  .anchor-card .ov-hl{{font-size:52px;color:#FF5A1F;margin-top:8px;letter-spacing:4px;}}
  .temp-chip{{right:120px;top:140px;font-family:'JetBrains Mono',monospace;font-size:66px;color:#FFF3E0;
    background:rgba(12,15,20,.4);padding:14px 26px;border-radius:8px;text-shadow:0 0 30px #FF5A1F;}}
  .water-bar{{left:0;right:0;bottom:130px;text-align:center;font-size:46px;color:#E8E6E1;
    text-shadow:0 2px 20px #000;}}
  .twoh{{left:0;right:0;bottom:150px;text-align:center;font-size:52px;color:#FFF3E0;}}
  .twoh b{{color:#FF5A1F;font-size:64px;}}
  .footer{{right:70px;bottom:60px;font-size:28px;color:#8a8f98;font-family:'JetBrains Mono',monospace;}}
  /* grade + grain + flash + blackout */
  #grade{{background:linear-gradient(180deg,rgba(61,157,246,.05),rgba(12,15,20,.25));
    mix-blend-mode:soft-light;box-shadow:inset 0 0 400px 120px rgba(0,0,0,.55);pointer-events:none;}}
  #grain{{opacity:.06;pointer-events:none;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/></filter><rect width='120' height='120' filter='url(%23n)'/></svg>");}}
  #flash{{background:#FFF3E0;opacity:0;pointer-events:none;}}
  #blackout{{background:#000;opacity:0;pointer-events:none;}}
</style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}">
    {shots_html}
    {ov_html}
    <div id="grade" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="8"></div>
    <div id="grain" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="9"></div>
    <div id="flash" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="10"></div>
    <div id="blackout" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="11"></div>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    (function(){{
      const tl = gsap.timeline({{ paused: true }});
      {timeline_js}
      window.__timelines["main"] = tl;
    }})();
  </script>
</body>
</html>
'''

open(f"{OUT}/index.html","w").write(HTML)
print(f"wrote index.html  shots={len(SHOTS)} overlays={len(OVERLAYS)} total={TOTAL}s")
