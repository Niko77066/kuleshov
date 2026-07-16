"""ir_migrate：M0 手写 film.json（三种方言）→ m1-v1 收编（DESIGN.md §2.4）。

方言语料：800v-thermal-runaway（voiceover 平铺、music.gen 字符串、seam 自由文本）、
samsung-health-ai-consent（overlays.range、source.group、provider heygen_avatar）、
estee-lauder-night（static_type、shot_ref/shot_refs/scope=all_shots、provider 变体）。

原则：只归一字段名与结构，不丢任何留痕——搬不动的键靠 extra=allow 原样保留。
"""

from __future__ import annotations

import copy
import re

from .models import SCHEMA_VERSION, STAGES
from .store import validate_dict

PROVIDER_MAP = {
    "image-motion": "image_motion",
    "heygen_avatar": "avatar",
    "stock_footage": "footage",
    "real_product_image": "footage",
}
ANCHOR_STATUS_MAP = {"captured": "acquired", "picked": "selected"}
_SEAM_PATTERNS = [
    (re.compile(r"^A|尾帧|续接|tail_relay"), "tail_relay"),
    (re.compile(r"^B|硬切|hard_cut"), "hard_cut"),
    (re.compile(r"^C|转场|擦除|transition|→MG|收尾"), "transition"),
]


def migrate(raw: dict) -> tuple[dict, list[str]]:
    """返回 (m1-v1 dict, 变更日志)。结尾全量 schema 校验，不过即抛。"""
    d = copy.deepcopy(raw)
    log: list[str] = []

    _meta(d, log)
    _voiceover(d, log)
    _music(d, log)
    _anchors(d, log)
    _shots(d, log)
    _groups(d, log)
    _overlays(d, log)
    _ledger(d, log)

    validated = validate_dict(d)
    return validated.dump(), log


def _meta(d: dict, log: list[str]) -> None:
    meta = d.setdefault("meta", {})
    if meta.get("schema_version") != SCHEMA_VERSION:
        meta["schema_version"] = SCHEMA_VERSION
        log.append(f"meta.schema_version → {SCHEMA_VERSION}")
    status = meta.get("status", "brief")
    if status not in (*STAGES, "delivered"):
        canonical = "delivered" if "deliver" in status else "brief"
        meta["status_original"] = status
        meta["status"] = canonical
        log.append(f"meta.status {status!r} → {canonical!r}（原值存 status_original）")


def _voiceover(d: dict, log: list[str]) -> None:
    vo = (d.get("audio") or {}).get("voiceover")
    if not isinstance(vo, dict):
        return
    # 800v 方言：生成留痕平铺在 voiceover 顶层
    if "gen" not in vo and "model" in vo:
        gen = {"model": vo.pop("model")}
        for src, dst in (("payload", "prompt_file"), ("gen_wallclock_s", "wallclock_s"),
                         ("duration_s", "duration_actual_s"), ("note", "note"),
                         ("response", "response"), ("format", "format"),
                         ("generated_once", "generated_once")):
            if src in vo:
                gen[dst] = vo.pop(src)
        if "voice_desc" in vo:
            vo["voice_profile"] = vo.pop("voice_desc")
        vo["gen"] = gen
        log.append("voiceover 平铺留痕 → gen 块（800v 方言）")
    gen = vo.get("gen")
    _fix_gen(gen, "voiceover", log)
    if isinstance(gen, dict) and "voice_profile" in gen and "voice_profile" not in vo:
        vo["voice_profile"] = gen["voice_profile"]


def _music(d: dict, log: list[str]) -> None:
    music = (d.get("audio") or {}).get("music")
    if isinstance(music, dict):
        if isinstance(music.get("gen"), str):
            music["gen"] = {"model": "", "note": music["gen"]}
            log.append("music.gen 字符串 → gen 块（note 保留原文）")
        _fix_gen(music.get("gen"), "music", log)


def _anchors(d: dict, log: list[str]) -> None:
    for a in d.get("anchors") or []:
        if "need" in a and "intent" not in a:
            a["intent"] = a.pop("need")
            log.append(f"anchors[{a.get('id')}].need → intent")
        st = a.get("status")
        if st in ANCHOR_STATUS_MAP:
            a["status"] = ANCHOR_STATUS_MAP[st]
            log.append(f"anchors[{a.get('id')}].status {st} → {a['status']}")
        if "picked_from" in a:
            note = a.get("note") or ""
            a["note"] = (note + f"；picked_from: {a.pop('picked_from')}").lstrip("；")
            log.append(f"anchors[{a.get('id')}].picked_from 并入 note")
        _fix_gen(a.get("gen"), f"anchors[{a.get('id')}]", log)


def _shots(d: dict, log: list[str]) -> None:
    for s in d.get("shots") or []:
        sid = s.get("id")
        src = s.get("source") or {}
        prov = src.get("provider")
        if prov in PROVIDER_MAP:
            src["provider"] = PROVIDER_MAP[prov]
            src.setdefault("params", {})["origin_provider"] = prov
            log.append(f"shots[{sid}].source.provider {prov} → {src['provider']}")
        if "group" in src and not s.get("group_ref"):
            s["group_ref"] = src.pop("group")
            log.append(f"shots[{sid}].source.group → group_ref")
        if "static_type" in s and "static_class" not in s:
            s["static_class"] = bool(s.pop("static_type"))
            log.append(f"shots[{sid}].static_type → static_class")
        _fix_gen(s.get("gen"), f"shots[{sid}]", log)


def _groups(d: dict, log: list[str]) -> None:
    for g in d.get("shot_groups") or []:
        for key in ("seam_out", "seam_in"):
            val = g.get(key)
            if isinstance(val, str) and val not in ("tail_relay", "hard_cut", "transition", "none"):
                parsed = next((name for pat, name in _SEAM_PATTERNS if pat.search(val)), None)
                if parsed:
                    g[key] = parsed
                    note = g.get("seam_note") or ""
                    g["seam_note"] = (note + f"；{key}: {val}").lstrip("；")
                    log.append(f"shot_groups[{g.get('id')}].{key} 自由文本 → {parsed}（原文存 seam_note）")
        # 回填成员镜头的 group_ref
        shots_by_id = {s.get("id"): s for s in d.get("shots") or []}
        for sid in g.get("shots") or []:
            s = shots_by_id.get(sid)
            if s is not None and not s.get("group_ref"):
                s["group_ref"] = g.get("id")


def _overlays(d: dict, log: list[str]) -> None:
    for o in d.get("overlays") or []:
        oid = o.get("id")
        if "range" in o and "shot_range" not in o:
            r = o.pop("range")
            if isinstance(r, list) and len(r) == 1:
                r = [r[0], r[0]]
            o["shot_range"] = r
            log.append(f"overlays[{oid}].range → shot_range")
        if "shot_ref" in o and "shot_range" not in o:
            ref = o.pop("shot_ref")
            o["shot_range"] = [ref, ref]
            log.append(f"overlays[{oid}].shot_ref → shot_range")
        if o.get("scope") in ("all_shots", "all"):
            o["scope"] = "global"
            log.append(f"overlays[{oid}].scope → global")
        if "provider" in o and "source" not in o:
            o["source"] = o.pop("provider")
        if "spec" in o and "intent" not in o:
            o["intent"] = o["spec"]


def _ledger(d: dict, log: list[str]) -> None:
    ledger = d.get("ledger") or {}
    for c in ledger.get("costs") or []:
        if "req_id" in c and "request_id" not in c:
            c["request_id"] = c.pop("req_id")
            log.append(f"costs[{c.get('id')}].req_id → request_id")
        if "usd_est" in c and "cost_usd" not in c:
            c["cost_usd"] = c["usd_est"]
            log.append(f"costs[{c.get('id')}].usd_est → cost_usd（原键保留）")
    for dec in ledger.get("decisions") or []:
        if "reason" in dec and "why" not in dec:
            dec["why"] = dec.pop("reason")
            log.append(f"decisions[{dec.get('id')}].reason → why")
    for g in ledger.get("gates") or []:
        if "gate" in g and "check" not in g:
            g["check"] = g.pop("gate")
            log.append(f"gates[{g.get('id')}].gate → check")


def _fix_gen(gen, owner: str, log: list[str]) -> None:
    if not isinstance(gen, dict):
        return
    if isinstance(gen.get("wallclock_s"), list):   # 多 take 数组（samsung 方言）
        takes = gen["wallclock_s"]
        gen["wallclock_s_each"] = takes
        gen["wallclock_s"] = round(sum(x for x in takes if isinstance(x, (int, float))), 1)
        log.append(f"{owner}.gen.wallclock_s 多 take 数组 → 求和（原值存 wallclock_s_each）")
    if "duration_probe_s" in gen and "duration_actual_s" not in gen:
        gen["duration_actual_s"] = gen["duration_probe_s"]
