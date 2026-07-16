"""TTS adapter：火山引擎 seed-audio-1.0（引擎知识包 tts-audio.md 的代码化）。

- 旁白整片一次生成（≤120s 上限内的 M1 默认；分节属 M2）；
- enable_subtitle=true → 逐字时间戳直接构建 audio.timeline；
- WhisperX 回转写校验不在本 adapter（它是独立证据，不能拿 TTS 自己的字幕当自己的证据）。
"""

from __future__ import annotations

import base64
import json
import os
import time
import urllib.request
from pathlib import Path

from ..errors import IRError, ENGINE_FAILURE, RULE_ZERO
from ..models import FilmIR
from .base import Adapter, Plan, RunResult, Target, find_repo_root, load_env

ENDPOINT = "https://openspeech.bytedance.com/api/v3/tts/create"
MODEL = "seed-audio-1.0"
MAX_PROMPT_CHARS = 3000    # API 硬限制
MAX_OUTPUT_S = 120         # API 硬限制
CN_CHARS_PER_S = 4.0       # 常速中文估读速，仅用于超限预警


class TTSAdapter(Adapter):
    name = "tts"
    mode = "audio"

    def _read_text_prompt(self, ir: FilmIR, project_dir: Path) -> str:
        vo = ir.audio.voiceover
        if vo is None or not vo.text_prompt_file:
            raise IRError(
                RULE_ZERO,
                "audio.voiceover.text_prompt_file 缺失——IR 里没有旁白输入就不许调 TTS",
                path="audio.voiceover.text_prompt_file",
                hint="先把〈声音档描述〉+「朗读：」+全文写入文件并回填该字段",
            )
        f = project_dir / vo.text_prompt_file
        if not f.is_file():
            raise IRError(RULE_ZERO, f"text_prompt_file 不存在: {f}",
                          path="audio.voiceover.text_prompt_file")
        return f.read_text(encoding="utf-8").strip()

    def plan(self, ir: FilmIR, target: Target, project_dir: Path) -> Plan:
        text = self._read_text_prompt(ir, project_dir)
        warnings = []
        if len(text) > MAX_PROMPT_CHARS:
            raise IRError(ENGINE_FAILURE,
                          f"text_prompt {len(text)} 字符，超 API 上限 {MAX_PROMPT_CHARS}",
                          hint="回 script 砍字（走正式修订），不许指望引擎宽容")
        est_s = len(text) / CN_CHARS_PER_S
        if est_s > MAX_OUTPUT_S * 0.92:
            warnings.append(f"估读 {est_s:.0f}s，逼近单次输出上限 {MAX_OUTPUT_S}s")
        payload = {
            "model": MODEL,
            "text_prompt": text,
            "audio_config": {"format": "mp3", "sample_rate": 48000, "pitch_rate": 0,
                             "speech_rate": 0, "loudness_rate": 0, "enable_subtitle": True},
            "watermark": {},
        }
        return Plan(target=target.raw, provider=self.name,
                    description=f"整片旁白 TTS（{len(text)} 字符 → audio/voiceover.mp3 + timeline）",
                    requests=[payload], est_cost_usd=None, warnings=warnings)

    def run(self, ir: FilmIR, target: Target, plan: Plan, project_dir: Path) -> RunResult:
        env = {**load_env(find_repo_root(project_dir)), **os.environ}
        api_key = env.get("VOLC_TTS_API_KEY")
        if not api_key:
            raise IRError(ENGINE_FAILURE, "缺 VOLC_TTS_API_KEY（仓库根 .env）",
                          hint="不造假产物糊弄下一阶段——配好 key 再跑")
        payload = plan.requests[0]
        req = urllib.request.Request(
            ENDPOINT, data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "X-Api-Key": api_key},
            method="POST")
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except Exception as e:  # 网络/HTTP 错误统一为可行动报错，不重试（铁律 5）
            raise IRError(ENGINE_FAILURE, f"TTS 调用失败: {e}",
                          hint="~20s 授权传播延迟会报 45000030，稍后由调用方决定是否重试") from e
        wallclock = round(time.monotonic() - t0, 1)

        audio_b64 = body.get("audio")
        if not audio_b64 and body.get("url"):
            with urllib.request.urlopen(body["url"], timeout=120) as r:
                audio_bytes = r.read()
        elif audio_b64:
            audio_bytes = base64.b64decode(audio_b64)
        else:
            raise IRError(ENGINE_FAILURE, f"响应无 audio 也无 url: {list(body)}")

        audio_dir = project_dir / "audio"
        audio_dir.mkdir(exist_ok=True)
        audio_file = audio_dir / "voiceover.mp3"
        audio_file.write_bytes(audio_bytes)

        timeline = _timeline_from_subtitle(body.get("subtitle") or {})
        timeline["file"] = "audio/timeline.json"
        timeline["source"] = "seed-audio subtitle（逐字）；WhisperX 回验另跑"
        (audio_dir / "timeline.json").write_text(
            json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")

        today = time.strftime("%Y-%m-%d")
        gen = {
            "model": MODEL,
            "prompt_file": ir.audio.voiceover.text_prompt_file,
            "params": payload["audio_config"],
            "date": today,
            "wallclock_s": wallclock,
            "duration_actual_s": timeline.get("duration_s"),
            "file": "audio/voiceover.mp3",
            "note": f"响应 duration={body.get('duration')} original_duration={body.get('original_duration')}",
        }
        cost_id = f"c{len(ir.ledger.costs) + 1:02d}"
        ops = [
            {"op": "set", "path": "audio.voiceover.file", "value": "audio/voiceover.mp3"},
            {"op": "set", "path": "audio.voiceover.gen", "value": gen},
            {"op": "set", "path": "audio.timeline", "value": timeline},
            {"op": "append", "path": "ledger.costs", "value": {
                "id": cost_id, "stage": "audio", "date": today, "item": "旁白全片 TTS",
                "model": MODEL,
                "note": f"计费口径 original_duration={body.get('original_duration')}",
            }},
        ]
        return RunResult(ops=ops,
                         artifacts=[str(audio_file), str(audio_dir / "timeline.json")],
                         summary=f"旁白 {timeline.get('duration_s')}s 落盘，timeline {len(timeline.get('sections', []))} 节")


def _timeline_from_subtitle(subtitle: dict) -> dict:
    """seed-audio subtitle（毫秒）→ audio.timeline（秒）。标点词条（零时长）过滤。"""
    sections, words = [], []
    for i, sent in enumerate(subtitle.get("sentences") or [], start=1):
        t0, t1 = sent.get("start_time", 0) / 1000, sent.get("end_time", 0) / 1000
        if t1 <= t0:
            continue
        sections.append({"id": f"sec{i:02d}", "t": [round(t0, 3), round(t1, 3)],
                         "text": sent.get("text", "")})
        for w in sent.get("words") or []:
            w0, w1 = w.get("start_time", 0) / 1000, w.get("end_time", 0) / 1000
            if w1 > w0:
                words.append({"w": w.get("text", ""), "t": [round(w0, 3), round(w1, 3)]})
    duration = sections[-1]["t"][1] if sections else 0.0
    return {"duration_s": duration, "sections": sections, "words": words,
            "words_count": len(words)}
