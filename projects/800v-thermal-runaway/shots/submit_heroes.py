#!/usr/bin/env python3
import os, json, urllib.request, urllib.error, re

BASE = os.environ['ARK_VIDEO_API_BASE_URL'].rstrip('/')
KEY  = os.environ['ARK_VIDEO_API_KEY']
MODEL = 'doubao-seedance-2-0-260128'
OUT = os.path.dirname(os.path.abspath(__file__))

URL_PACK  = 'https://storage.neodrop.ai/kuleshov/800v-thermal-runaway/a02_pack.png'
URL_CELL  = 'https://storage.neodrop.ai/kuleshov/800v-thermal-runaway/a03_module.png'
URL_STYLE = 'https://storage.neodrop.ai/kuleshov/800v-thermal-runaway/a01_styleframe.png'

STYLE = ("Forensic engineering-documentary cinematography. Deep carbon-black (#0C0F14) environment, "
 "low-key dramatic raking light. Heat reads as ONE color ramp only - amber #FFB02E to orange #FF5A1F "
 "to white-hot #FFF3E0; cool coolant-blue #3D9DF6 only on still-normal parts. Bone-white crisp edge "
 "highlights. Physically real brushed-metal and matte materials, shallow depth of field, subtle "
 "volumetric haze. NO text, NO logos, NO on-screen labels, NO rainbow colors, NO sci-fi HUD, "
 "NO blue particle FX, NO cartoon look.")
AUDIO = ("No BGM, no music, no score. Diegetic ambience and synchronized physical SFX only. "
 "No dialogue or narration.")

def P(subjects, env, cont, timeline):
    return (f"SUBJECTS\n{subjects}\n\nENVIRONMENT\n{env}\n\nSTYLE\n{STYLE}\n\n"
            f"CONTINUITY\n{cont}\n\nAUDIO RULE\n{AUDIO}\n\nTIMELINE\n{timeline}")

shots = {
 "s01-A": dict(refs=[("image_url",URL_PACK),("image_url",URL_STYLE)], duration=8, prompt=P(
   "An 800V lithium battery pack @Image1 (a row of dark prismatic cells with metal terminal posts in a dark-metal tray); one central cell faintly glowing amber from within, a thin vapor wisp at its vent. Style/lighting reference @Image2.",
   "Pitch-black forensic investigation studio, matte floor, single soft key from upper-left, faint haze catching the light.",
   "Keep @Image1 pack and cell design exact. One and only one cell is heating; the rest read cool-blue normal. Damage state: earliest onset, no flame yet.",
   ("0:00-0:03 Wide establishing, slow dolly-in on the whole pack in darkness. Only faint blue rim on cells; the central cell just beginning to warm. SFX: deep room tone, faint electrical hum.\n"
    "0:03-0:06 Medium, continued dolly-in, the one amber cell brightening subtly, vapor thread rising. SFX: low hum, faint tick of expanding metal.\n"
    "0:06-0:08 HARD-CUT END FRAME: locked medium-close on the glowing cell centered, camera fully settled, amber core steady, vapor frozen mid-rise, cool-blue neighbors. Hold 0.5s. No fade, dissolve, morph, or camera drift. SFX: hum resolves into room tone."))),
 "s01-B": dict(refs=[("image_url",URL_PACK),("image_url",URL_STYLE)], duration=8, prompt=P(
   "An 800V lithium battery pack @Image1 (a row of dark prismatic cells with metal terminal posts in a dark-metal tray); one cell faintly glowing amber from within, thin vapor at its vent. Style/lighting reference @Image2.",
   "Pitch-black forensic studio, low camera height, stronger haze, generous negative space above the pack.",
   "Keep @Image1 pack and cell design exact. Exactly one cell is heating; others cool-blue normal. Earliest onset, no flame.",
   ("0:00-0:03 Low-angle wide, slow push-in along the tray toward the pack, silhouettes rimmed cool-blue. SFX: deep room tone.\n"
    "0:03-0:06 Rack focus lands on the single amber cell as the push continues; internal glow pulses once, vapor rising. SFX: faint hum, soft crackle.\n"
    "0:06-0:08 HARD-CUT END FRAME: locked close on the amber cell off-center right, camera settled, glow steady, haze drifting, neighbors cool-blue. Hold 0.5s. No fade, dissolve, morph, or camera drift. SFX: settles to room tone."))),
 "s05-A": dict(refs=[("image_url",URL_CELL),("image_url",URL_STYLE)], duration=8, prompt=P(
   "A single 800V prismatic battery cell @Image1 in thermal runaway, its top safety vent rupturing; a high-velocity jet of hot grey-white gas and sparks blasts out. Style/lighting reference @Image2.",
   "Dark forensic studio, the cell isolated on a matte stage, deep black background, volumetric haze lit from the side.",
   "Keep @Image1 cell design exact. Cell body glows orange intensifying to white-hot at the vent; the jet is pressurized and directional, not a soft puff. Hot gas only, no open flame.",
   ("0:00-0:02 Medium side view, locked; the vent bulges, first spurt of gas escapes, cell body reddening. SFX: rising metallic groan, pressure hiss building.\n"
    "0:02-0:05 Slow-motion side tracking; the vent ruptures fully, a violent directional gas jet with sparks blasts sideways, body glowing orange-to-white. SFX: sharp explosive hiss, spark spatter.\n"
    "0:05-0:08 HARD-CUT END FRAME: locked medium-close, camera settled, jet sustained and readable, white-hot vent centered, glowing cell body, gas streaming. Hold 0.5s. No fade, dissolve, morph, or camera drift. SFX: sustained roaring hiss into steady jet noise."))),
 "s05-B": dict(refs=[("image_url",URL_CELL),("image_url",URL_STYLE)], duration=8, prompt=P(
   "A single 800V prismatic battery cell @Image1 in thermal runaway, top safety vent rupturing; a high-velocity jet of hot gas and sparks erupts upward. Style/lighting reference @Image2.",
   "Dark forensic studio, three-quarter high angle looking slightly down at the vent so the jet climbs toward camera, deep black background, side-lit haze.",
   "Keep @Image1 cell design exact. Body glows orange to white-hot at the vent; directional pressurized jet, hot gas only, no open flame.",
   ("0:00-0:02 Three-quarter high, locked; vent seams glowing, pressure swelling under the cap. SFX: metallic groan, hiss building.\n"
    "0:02-0:05 Slow-motion, slight crash-zoom in as the vent bursts and a gas-and-spark jet erupts upward toward camera, body flashing white-hot. SFX: explosive rupture, sparks.\n"
    "0:05-0:08 HARD-CUT END FRAME: locked three-quarter close, camera settled, jet plume readable rising out of top of frame, white-hot vent, orange body. Hold 0.5s. No fade, dissolve, morph, or camera drift. SFX: roaring jet into steady hiss."))),
}

def submit(name, s):
    content = [{"type": t, t: {"url": u}, "role": "reference_image"} for (t, u) in s["refs"]]
    payload = {"model": MODEL, "prompt": s["prompt"],
               "metadata": {"content": content, "resolution": "1080p", "ratio": "16:9", "generate_audio": False},
               "duration": s["duration"]}
    json.dump(payload, open(f"{OUT}/payload-{name}.json", "w"), ensure_ascii=False, indent=1)
    req = urllib.request.Request(f"{BASE}/v1/videos", data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = json.load(r); rid = r.headers.get("x-oneapi-request-id")
    except urllib.error.HTTPError as e:
        print(f"{name}: HTTP {e.code} {e.read().decode()[:300]}"); return None
    tid = body.get("id") or body.get("task_id")
    rec = {"name": name, "task_id": tid, "status": body.get("status"), "request_id": rid, "duration_req": s["duration"]}
    json.dump({**rec, "submit_response": body}, open(f"{OUT}/submit-{name}.json", "w"), ensure_ascii=False, indent=1)
    print(f"{name}: task_id={tid} status={body.get('status')} rid={rid}")
    return rec

if __name__ == "__main__":
    recs = [submit(n, s) for n, s in shots.items()]
    json.dump([r for r in recs if r], open(f"{OUT}/heroes-submitted.json", "w"), ensure_ascii=False, indent=1)
