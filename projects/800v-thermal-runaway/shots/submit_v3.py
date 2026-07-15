#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v3 Seedance regen — 2-2-video discipline: multi-shot per clip (>=2 cuts / 5s),
visual spectacle, fast pace, LOCKED HARD-CUT END FRAME (~1.5s hold so tail-trim to slot
still lands on a resolved frame). duration in metadata = ceil(slot)."""
import os, json, subprocess, sys
BASE=os.environ['ARK_VIDEO_API_BASE_URL'].rstrip('/'); KEY=os.environ['ARK_VIDEO_API_KEY']
MODEL='doubao-seedance-2-0-260128'; OUT=os.path.dirname(os.path.abspath(__file__))
U="https://storage.neodrop.ai/kuleshov/800v-thermal-runaway/"
PACK,CELL,STYLE=U+"a02_pack.png",U+"a03_module.png",U+"a01_styleframe.png"
STYLE_B=("Forensic engineering-documentary cinematography with HIGH VISUAL IMPACT and dynamic scale. "
 "Deep carbon-black (#0C0F14), low-key dramatic light. Heat is ONE ramp only: amber #FFB02E -> orange #FF5A1F "
 "-> white-hot #FFF3E0; cool coolant-blue #3D9DF6 only on still-normal parts. Bone-white crisp edges. "
 "Physically real brushed metal, macro detail, volumetric haze, fast decisive camera. NO text, NO logos, "
 "NO on-screen labels, NO rainbow, NO sci-fi HUD, NO blue particle FX, NO cartoon look.")
AUDIO_B="No BGM, no music. Diegetic ambience and synchronized physical SFX only. No dialogue or narration."
def P(subj,env,cont,tl): return f"SUBJECTS\n{subj}\n\nENVIRONMENT\n{env}\n\nSTYLE\n{STYLE_B}\n\nCONTINUITY\n{cont}\n\nAUDIO RULE\n{AUDIO_B}\n\nTIMELINE\n{tl}"

S={
"s01":dict(dur=7,refs=[PACK,STYLE],prompt=P(
 "An 800V lithium battery pack @Image1 (row of dark prismatic cells, metal posts, dark tray); ONE cell heating amber from within with a vapor curl. Style/light ref @Image2.",
 "Pitch-black forensic studio, volumetric haze, deep negative space.",
 "Keep @Image1 exact. Exactly one cell heats; others cool-blue. Earliest onset, no flame. Fast, punchy cutting between framings.",
 "0:00-0:02 WIDE, fast dolly-in through darkness toward the pack, cells rimmed cool-blue. SFX: deep room tone rising.\n"
 "0:02-0:035 HARD CUT to extreme MACRO insert of the one cell's vent: first amber glow blooms, a vapor thread curls up, rack focus snap. SFX: faint tick, hiss.\n"
 "0:035-0:055 HARD CUT to low 3/4 MEDIUM: the amber cell pulses brighter among cool-blue neighbors, haze drifting. SFX: low electrical hum.\n"
 "0:055-0:07 HARD-CUT END FRAME: locked medium-close on the single amber cell centered, camera fully settled, glow steady, vapor frozen mid-rise, cool-blue neighbors. Hold 1.4s. No fade/dissolve/morph/drift. SFX: settles to room tone.")),
"s04":dict(dur=8,refs=[CELL,STYLE],prompt=P(
 "Extreme macro INSIDE a prismatic cell @Image1: wound electrode-and-separator layers; polymer separator melting; anode and cathode touch; short-circuit spark; heat bloom. Style/light ref @Image2.",
 "Microscopic interior, black voids between layers, hot glow the only light, drifting particulate.",
 "Keep @Image1 layer look. Progression melt->contact->spark->bloom. Hot gas/sparks only, no flame. Rapid macro cuts.",
 "0:00-0:02 EXTREME MACRO, fast drift across layers; the separator film sags, shrinks, edges curling amber. SFX: sizzle, creak.\n"
 "0:02-0:04 HARD CUT tighter INSERT: anode and cathode layers snap together, a violent white-hot short-circuit spark bursts. SFX: electric snap.\n"
 "0:04-0:065 HARD CUT: heat bloom races outward through the wound layers, sparks scattering, glow intensifying. SFX: crackle building.\n"
 "0:065-0:08 HARD-CUT END FRAME: locked extreme close on the white-hot micro-arc point radiating, layers silhouetted, camera settled. Hold 1.5s. No fade/dissolve/morph/drift. SFX: crackle into low roar.")),
"s05":dict(dur=8,refs=[CELL,STYLE],prompt=P(
 "A single 800V prismatic cell @Image1 in thermal runaway; side casing ruptures exposing glowing jelly-roll; violent sideways jet of sparks and hot grey-white gas. Style/light ref @Image2.",
 "Dark forensic studio, cell on a matte stage among a few neighbors, black background, side-lit haze.",
 "Keep @Image1 exact. Body orange->white-hot; rupture exposes internal layers; pressurized directional jet, hot gas/sparks only, no flame. Explosive pacing.",
 "0:00-0:015 MEDIUM side, locked; body reddening, casing seam bulging under pressure. SFX: metallic groan, pressure hiss.\n"
 "0:015-0:03 HARD CUT CLOSE: the side casing bursts open, exposed jelly-roll layers glow white-hot. SFX: sharp rupture crack.\n"
 "0:03-0:055 HARD CUT WIDER slow-mo: a violent spark-and-gas jet blasts sideways, debris flung, body flashing white. SFX: explosive hiss, spark spatter.\n"
 "0:055-0:08 HARD-CUT END FRAME: locked medium, sideways jet sustained and readable, exposed white-hot electrodes centered, glowing body, camera settled. Hold 1.4s. No fade/dissolve/morph/drift. SFX: roaring jet into steady hiss.")),
"s08":dict(dur=7,refs=[PACK,STYLE],prompt=P(
 "An 800V battery pack @Image1 close along its row; thermal runaway propagating cell to cell like dominoes, heat color spreading to neighbors, vapor rising. Style/light ref @Image2.",
 "Pitch-black studio, camera low and close along the row receding into darkness, volumetric haze.",
 "Keep @Image1 exact. Clear directional wave: hot cells white/orange, next igniting amber, far cells cool-blue. No flame. Fast dynamic cuts.",
 "0:00-0:02 CLOSE tracking along the row, first cell white-hot, adjacent flaring orange, heat creeping. SFX: low roar, ticking metal.\n"
 "0:02-0:04 HARD CUT OVERHEAD: the heat wave visibly jumps one more cell, a clean domino read down the row. SFX: escalating crackle.\n"
 "0:04-0:055 HARD CUT LOW ANGLE: vapor thickening, the next cell igniting amber, cool-blue cells waiting ahead. SFX: hiss, rumble.\n"
 "0:055-0:07 HARD-CUT END FRAME: locked medium on three or four hot cells with the very next just starting to glow amber, camera settled. Hold 1.4s. No fade/dissolve/morph/drift. SFX: sustained roar.")),
"s11":dict(dur=6,refs=[STYLE],prompt=P(
 "Macro dark: a high-voltage copper busbar and insulation between cells; insulation chars and cracks; a blinding electric arc snaps across the gap and ignites escaping gas. Style/light ref @Image1.",
 "Pitch-black interior; only charring glow and the arc as light; heavy haze from escaping gas.",
 "800V high-voltage. Progression char->arc->ignite. The arc is a blinding blue-white discharge (the ONE allowed non-heat light). End on a bright flash. Sharp fast cuts.",
 "0:00-0:015 MACRO creep to the busbar; insulation blackening, cracking, faint orange heat at edges. SFX: crackle, rising buzz.\n"
 "0:015-0:03 HARD CUT: a sudden blinding electric arc snaps across the charred gap, sparks explode outward. SFX: sharp electrical crack.\n"
 "0:03-0:045 HARD CUT: the arc ignites a puff of escaping gas with a flare, light blasting the frame. SFX: ignition whoomp.\n"
 "0:045-0:06 HARD-CUT END FRAME: the arc flash at peak brightness nearly whiting the frame, camera locked. Hold 0.4s. No fade/dissolve/morph/drift. SFX: crack peaks then cuts.")),
"s12":dict(dur=9,refs=[],prompt=P(
 "Night: firefighters aim powerful hoses at the smoking underbody of an electric car; thousands of litres sheet off the battery pack, but grey smoke keeps pouring out.",
 "Outdoor night, wet asphalt reflecting emergency light, car low in frame, dense smoke/steam, water spray catching light.",
 "Documentary realism, carbon-black night, cool tones except a dull orange glow persisting under the car. No faces in focus, no text, no logos. Urgent pacing.",
 "0:00-0:025 WIDE handheld, water jets slam the car underbody, huge steam-and-smoke clouds billow. SFX: roaring water, hissing steam.\n"
 "0:025-0:05 HARD CUT CLOSER: water sheets off the pack but a dull orange glow persists deep inside. SFX: water roar, low internal rumble.\n"
 "0:05-0:075 HARD CUT LOW at asphalt level: runoff and reflections, smoke unrelenting above. SFX: splatter, hiss.\n"
 "0:075-0:09 HARD-CUT END FRAME: locked medium on water sheeting off the underbody while smoke still rises and the ember glow remains, camera settled. Hold 1.4s. No fade/dissolve/morph/drift. SFX: steady water and steam.")),
"s15":dict(dur=7,refs=[PACK,STYLE],prompt=P(
 "The same 800V pack @Image1 as the opening, now calming: the one cell's glow fading to a dull ember, thin smoke settling, whole pack intact and dark. Style/light ref @Image2.",
 "Pitch-black studio, same low-key light as the opening, haze thinning.",
 "Keep @Image1 exact — same pack as the opening for a bookend. Damage contained to one cell; neighbors stayed cool-blue. Calm resolution, no active flame/jet.",
 "0:00-0:02 MEDIUM-CLOSE on the ember cell, glow dimming orange->dull red, last vapor curling. SFX: settling ticks, fading hiss.\n"
 "0:02-0:04 HARD CUT: slow pull-out begins revealing the intact pack in its tray. SFX: quiet room tone.\n"
 "0:04-0:055 HARD CUT WIDE: the whole pack settled, the single contained cell the only warm point among cool-blue neighbors. SFX: low room tone.\n"
 "0:055-0:07 HARD-CUT END FRAME: locked wide on the settled pack, one faint sealed glow, camera fully still. Hold 1.4s. No fade/dissolve/morph/drift. SFX: low room tone.")),
}
def submit(name,s):
    meta={"resolution":"1080p","ratio":"16:9","generate_audio":False,"duration":s["dur"]}
    if s["refs"]: meta["content"]=[{"type":"image_url","image_url":{"url":u},"role":"reference_image"} for u in s["refs"]]
    json.dump({"model":MODEL,"prompt":s["prompt"],"metadata":meta},open(f"{OUT}/payload3-{name}.json","w"),ensure_ascii=False,indent=1)
    r=subprocess.run(["curl","-sS","--max-time","60","-X","POST",f"{BASE}/v1/videos","-H","Content-Type: application/json",
      "-H",f"Authorization: Bearer {KEY}","--data-binary",f"@{OUT}/payload3-{name}.json","-D",f"{OUT}/sub3-{name}-hdr.txt"],capture_output=True,text=True)
    try: b=json.loads(r.stdout)
    except: print(f"{name}: parse err {r.stdout[:200]}"); return None
    tid=b.get("id") or b.get("task_id"); rid=""
    for ln in open(f"{OUT}/sub3-{name}-hdr.txt",errors="ignore"):
        if ln.lower().startswith("x-oneapi-request-id"): rid=ln.split(":",1)[1].strip()
    print(f"{name}: dur={s['dur']} task_id={tid} status={b.get('status')} rid={rid}"); return {"name":name,"task_id":tid,"rid":rid}
if __name__=="__main__":
    only=sys.argv[1:] or list(S)
    recs=[submit(n,S[n]) for n in only]
    json.dump([r for r in recs if r],open(f"{OUT}/v3-submitted.json","w"),ensure_ascii=False,indent=1)
    print("POLL:"," ".join(f"{r['name']}={r['task_id']}" for r in recs if r))
