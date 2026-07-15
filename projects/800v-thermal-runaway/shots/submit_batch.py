#!/usr/bin/env python3
"""Regenerate chosen heroes at planned length + batch-2 shots. duration goes in metadata.
Submit via curl (python urllib hits Cloudflare 1010)."""
import os, json, subprocess, sys

BASE = os.environ['ARK_VIDEO_API_BASE_URL'].rstrip('/')
KEY  = os.environ['ARK_VIDEO_API_KEY']
MODEL = 'doubao-seedance-2-0-260128'
OUT = os.path.dirname(os.path.abspath(__file__))
U = "https://storage.neodrop.ai/kuleshov/800v-thermal-runaway/"
PACK, CELL, STYLE = U+"a02_pack.png", U+"a03_module.png", U+"a01_styleframe.png"

STYLE_B = ("Forensic engineering-documentary cinematography. Deep carbon-black (#0C0F14) environment, "
 "low-key dramatic raking light. Heat reads as ONE color ramp only - amber #FFB02E to orange #FF5A1F "
 "to white-hot #FFF3E0; cool coolant-blue #3D9DF6 only on still-normal parts. Bone-white crisp edge "
 "highlights. Physically real brushed-metal and matte materials, shallow depth of field, subtle "
 "volumetric haze. NO text, NO logos, NO on-screen labels, NO rainbow colors, NO sci-fi HUD, "
 "NO blue particle FX, NO cartoon look.")
AUDIO_B = "No BGM, no music, no score. Diegetic ambience and synchronized physical SFX only. No dialogue or narration."

def P(subj, env, cont, tl):
    return f"SUBJECTS\n{subj}\n\nENVIRONMENT\n{env}\n\nSTYLE\n{STYLE_B}\n\nCONTINUITY\n{cont}\n\nAUDIO RULE\n{AUDIO_B}\n\nTIMELINE\n{tl}"

shots = {
 # s01 — chosen approach B (single cell, restrained), at planned length
 "s01": dict(dur=8, refs=[PACK, STYLE], prompt=P(
   "An 800V lithium battery pack @Image1 (row of dark prismatic cells, metal terminal posts, in a dark-metal tray); ONE cell glowing amber from within, thin vapor at its vent. Style/lighting reference @Image2.",
   "Pitch-black forensic studio, low camera height, strong volumetric haze, generous negative space above the pack.",
   "Keep @Image1 pack and cell design exact. EXACTLY ONE cell heats; all others stay cool-blue normal. Earliest onset, no flame, no spread to neighbors.",
   ("0:00-0:03 Low-angle wide, slow push-in along the tray; cells rimmed cool-blue in darkness. SFX: deep room tone.\n"
    "0:03-0:055 Rack focus settles on the single amber cell, shallow depth of field; its internal glow swells slightly, one vapor thread rising. SFX: faint electrical hum, soft tick of expanding metal.\n"
    "0:055-0:08 HARD-CUT END FRAME: locked medium-close on the one amber cell off-center, camera fully settled, glow steady, haze drifting, neighbors cool-blue. Hold 0.6s. No fade, dissolve, morph, or camera drift. SFX: settles to room tone."))),
 # s04 — extreme macro separator melt / internal short
 "s04": dict(dur=8, refs=[CELL, STYLE], prompt=P(
   "Extreme macro inside a prismatic cell @Image1: wound electrode-and-separator layers; the thin polymer separator melting and shrinking, letting anode and cathode layers touch. Style/lighting reference @Image2.",
   "Microscopic interior, pitch-black voids between layers, hot glow the only light, drifting particulate haze.",
   "Keep @Image1 internal layer look. Progression: melt -> contact -> short-circuit spark -> heat bloom. Single micro-event, hot gas and sparks only, no open flame.",
   ("0:00-0:03 Extreme macro, slow drift across the layered structure; the separator film sags and shrinks under heat, edges curling amber. SFX: faint sizzle, material creak.\n"
    "0:03-0:06 Rack focus as anode and cathode layers touch — a sharp short-circuit spark bursts, white-hot, heat glow blooming outward through the layers. SFX: electric snap, crackle.\n"
    "0:06-0:08 HARD-CUT END FRAME: locked extreme close on the white-hot micro-arc point, camera settled, glow radiating, layers silhouetted. Hold 0.5s. No fade, dissolve, morph, or camera drift. SFX: crackle into low roar."))),
 # s05 — chosen approach A (side burst, exposed jelly-roll, sideways jet), at planned length
 "s05": dict(dur=8, refs=[CELL, STYLE], prompt=P(
   "A single 800V prismatic battery cell @Image1 in thermal runaway; its casing ruptures on the side exposing the glowing wound jelly-roll electrodes, and a violent jet of sparks and hot grey-white gas blasts sideways. Style/lighting reference @Image2.",
   "Dark forensic studio, the cell isolated on a matte stage among a few neighbors, deep black background, side-lit volumetric haze.",
   "Keep @Image1 cell design exact. Body glows orange to white-hot; the rupture exposes internal layers; pressurized directional jet, hot gas and sparks only, no open flame.",
   ("0:00-0:02 Medium side view, locked; the cell body reddens, casing seam bulging under pressure. SFX: rising metallic groan, pressure hiss.\n"
    "0:02-0:055 Slow-motion side tracking; the side casing ruptures, exposed jelly-roll layers glow white-hot, a violent spark-and-gas jet blasts sideways. SFX: explosive rupture, spark spatter.\n"
    "0:055-0:08 HARD-CUT END FRAME: locked medium-close, camera settled, sideways jet sustained and readable, exposed white-hot electrode layers centered, glowing body. Hold 0.5s. No fade, dissolve, morph, or camera drift. SFX: roaring jet into steady hiss."))),
 # s08 — in-pack cell-to-cell propagation
 "s08": dict(dur=8, refs=[PACK, STYLE], prompt=P(
   "An 800V battery pack @Image1 seen close along its row of prismatic cells; thermal runaway propagating cell to cell — heat color spreading from one glowing cell to its neighbors in sequence like dominoes, vapor rising. Style/lighting reference @Image2.",
   "Pitch-black forensic studio, camera low and close along the row so cells recede into darkness, volumetric haze.",
   "Keep @Image1 pack and cell design exact. A clear directional wave: already-hot cells white/orange, the next cell just igniting amber, far cells still cool-blue. Hot gas only, no open flame.",
   ("0:00-0:03 Close tracking along the row; the first cell white-hot, the adjacent one flaring orange, heat visibly creeping to the next. SFX: low roar, ticking of heating metal.\n"
    "0:03-0:06 Continue the slow push; the wave advances one more cell, vapor thickening, cool-blue cells ahead waiting. SFX: escalating crackle, hiss.\n"
    "0:06-0:08 HARD-CUT END FRAME: locked medium on three or four hot cells with the very next just starting to glow amber, camera settled. Hold 0.5s. No fade, dissolve, morph, or camera drift. SFX: sustained roar."))),
 # s11 — HV busbar arc (macro dark)
 "s11": dict(dur=6, refs=[STYLE], prompt=P(
   "Macro dark shot of a high-voltage copper busbar and its insulation between battery cells; the insulation chars and cracks from heat, then a blinding electric arc snaps across the gap, igniting escaping gas. Style/lighting reference @Image1.",
   "Pitch-black interior, only the charring glow and the arc as light sources, heavy haze from escaping gas.",
   "800V high-voltage context. Progression: insulation carbonizes -> arc strikes -> gas ignites. The arc is a blinding blue-white electrical discharge (this is the ONE allowed non-heat-ramp light). Ends on a bright flash for a hard cut.",
   ("0:00-0:025 Macro, slow creep toward the busbar; insulation blackening and cracking, faint orange heat at the edges. SFX: crackle, rising electrical buzz.\n"
    "0:025-0:05 A sudden blinding electric arc snaps across the charred gap, igniting a puff of gas with a flare. SFX: sharp electrical crack, ignition whoomp.\n"
    "0:05-0:06 HARD-CUT END FRAME: the arc flash at peak brightness nearly whiting the frame, camera locked. Hold 0.3s. No fade, dissolve, morph, or camera drift. SFX: electrical crack peaks then cuts."))),
 # s12 — firefighters hosing car underbody (text-to-video, no ref)
 "s12": dict(dur=10, refs=[], prompt=P(
   "Night scene: firefighters aiming powerful hoses at the smoking underbody of an electric car, thousands of litres of water sheeting off the battery pack, but grey smoke keeps pouring out and refuses to relent.",
   "Outdoor at night, wet asphalt reflecting emergency light, the car low in frame, dense smoke and steam, water spray catching the light.",
   "Documentary realism, deep carbon-black night, cool tones except the dull orange glow stubbornly persisting under the car. Water in front, heat within — a feeling of futility. No people's faces in focus, no text, no logos.",
   ("0:00-0:03 Wide handheld, water jets hitting the car underbody, huge clouds of steam and smoke billowing. SFX: roaring water, hissing steam.\n"
    "0:03-0:07 Slow push toward the underbody; water sheets off but a dull orange glow persists deep inside, smoke unrelenting. SFX: water roar, low internal rumble.\n"
    "0:07-0:10 HARD-CUT END FRAME: locked medium on water sheeting off the underbody while smoke still rises and the ember glow remains, camera settled. Hold 0.6s. No fade, dissolve, morph, or camera drift. SFX: steady water and steam hiss."))),
 # s15 — closing hero, echo of s01, pack now calm
 "s15": dict(dur=8, refs=[PACK, STYLE], prompt=P(
   "The same 800V battery pack @Image1 as the opening, now calming down: the one cell's glow contained and fading to a dull ember, thin smoke settling, the whole pack intact and dark. Style/lighting reference @Image2.",
   "Pitch-black forensic studio, matte floor, same low-key light as the opening, haze thinning.",
   "Keep @Image1 pack and cell design exact — visually the same pack as the opening shot for a bookend. Damage contained to one cell; neighbors stayed cool-blue normal. Resolution/calm, no active flame or jet.",
   ("0:00-0:03 Medium-close on the ember cell, its glow dimming from orange toward dull red, last vapor curling away. SFX: settling ticks, fading hiss.\n"
    "0:03-0:06 Slow pull-out revealing the whole intact pack in the tray, the single contained cell the only warm point among cool-blue neighbors. SFX: quiet room tone.\n"
    "0:06-0:08 HARD-CUT END FRAME: locked wide on the settled pack, one faint sealed glow, camera fully still. Hold 0.7s. No fade, dissolve, morph, or camera drift. SFX: low room tone."))),
}

def submit(name, s):
    content = [{"type":"image_url","image_url":{"url":u},"role":"reference_image"} for u in s["refs"]]
    meta = {"resolution":"1080p","ratio":"16:9","generate_audio":False,"duration":s["dur"]}
    if content: meta["content"] = content
    payload = {"model":MODEL,"prompt":s["prompt"],"metadata":meta}
    json.dump(payload, open(f"{OUT}/payload2-{name}.json","w"), ensure_ascii=False, indent=1)
    r = subprocess.run(["curl","-sS","--max-time","60","-X","POST",f"{BASE}/v1/videos",
        "-H","Content-Type: application/json","-H",f"Authorization: Bearer {KEY}",
        "--data-binary",f"@{OUT}/payload2-{name}.json","-D",f"{OUT}/sub2-{name}-hdr.txt"],
        capture_output=True, text=True)
    try: body = json.loads(r.stdout)
    except Exception: print(f"{name}: parse err {r.stdout[:200]}"); return None
    tid = body.get("id") or body.get("task_id")
    rid = ""
    for line in open(f"{OUT}/sub2-{name}-hdr.txt", errors="ignore"):
        if line.lower().startswith("x-oneapi-request-id"): rid = line.split(":",1)[1].strip()
    rec = {"name":name,"task_id":tid,"status":body.get("status"),"request_id":rid,"dur_req":s["dur"]}
    print(f"{name}: dur={s['dur']} task_id={tid} status={body.get('status')} rid={rid}")
    return rec

if __name__ == "__main__":
    only = sys.argv[1:] or list(shots)
    recs = [submit(n, shots[n]) for n in only]
    json.dump([r for r in recs if r], open(f"{OUT}/batch2-submitted.json","w"), ensure_ascii=False, indent=1)
    print("submitted:", " ".join(f"{r['name']}={r['task_id']}" for r in recs if r))
