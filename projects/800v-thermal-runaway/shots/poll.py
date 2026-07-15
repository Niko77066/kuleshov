#!/usr/bin/env python3
"""Poll Seedance tasks to terminal state, download completed clips, emit one line per event.
Usage: poll.py <name>=<task_id> [<name>=<task_id> ...]"""
import os, sys, json, time, subprocess

BASE = os.environ['ARK_VIDEO_API_BASE_URL'].rstrip('/')
KEY  = os.environ['ARK_VIDEO_API_KEY']
OUT  = os.path.dirname(os.path.abspath(__file__))

def get(task_id):
    # curl (python urllib gets Cloudflare 1010)
    r = subprocess.run(["curl","-sS","--max-time","40","-H",f"Authorization: Bearer {KEY}",
                        f"{BASE}/v1/videos/{task_id}"], capture_output=True, text=True)
    try: return json.loads(r.stdout)
    except Exception: return {"status":"__parse_error__","raw":r.stdout[:200]}

def dl(url, path):
    subprocess.run(["curl","-sS","--max-time","180","-o",path,url], check=True)

def ffdur(path):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","default=noprint_wrappers=1:nokey=1",path], capture_output=True, text=True)
    try: return round(float(r.stdout.strip()),3)
    except Exception: return None

tasks = dict(a.split("=",1) for a in sys.argv[1:])
done = {}
print(f"polling {len(tasks)} tasks", flush=True)
while len(done) < len(tasks):
    for name, tid in tasks.items():
        if name in done: continue
        d = get(tid)
        st = d.get("status")
        if st in ("completed","succeeded","success"):
            url = (d.get("metadata") or {}).get("url") or d.get("url")
            mp4 = f"{OUT}/{name}.mp4"
            info = {"name":name,"task_id":tid,"status":st,"url":url,"meta_duration":(d.get("metadata") or {}).get("duration")}
            if url:
                try:
                    dl(url, mp4); info["file"]=f"shots/{name}.mp4"; info["duration_actual_s"]=ffdur(mp4)
                except Exception as e:
                    info["download_error"]=str(e)
            json.dump(d, open(f"{OUT}/result-{name}.json","w"), ensure_ascii=False, indent=1)
            done[name]=info
            print(f"EVENT {name}: COMPLETED dur={info.get('duration_actual_s')}s file={info.get('file')}", flush=True)
        elif st in ("failed","error","cancelled","canceled"):
            json.dump(d, open(f"{OUT}/result-{name}.json","w"), ensure_ascii=False, indent=1)
            done[name]={"name":name,"status":st,"detail":json.dumps(d)[:300]}
            print(f"EVENT {name}: FAILED {json.dumps(d)[:200]}", flush=True)
    if len(done) < len(tasks):
        time.sleep(20)
json.dump(list(done.values()), open(f"{OUT}/heroes-results.json","w"), ensure_ascii=False, indent=1)
print("ALL DONE", flush=True)
