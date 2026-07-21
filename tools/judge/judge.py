#!/usr/bin/env python3
"""G2 评委（Kimi K3 · API 直调）：hero-frame 门与成片门两节点盲评。

隔离纪律：只读证据包；扣分必须引用镜头 ID / 时间码，缺引用判无效
（LLM 无锚点自评 ~46% 准确率，styles/_iteration.md）。评委只产报告，
不改 film.json——报告由 SOP 席位 append 进 ledger.gates。

网络注意：网关 Cloudflare 拦 python-urllib UA（hf 片实证），故走 curl + 文件负载。
kimi-k3 是推理模型：思考计费（reasoning_tokens），解析只取 message.content。

模型链（2026-07-21 拍板）：kimi-k3（contact sheet 图片证据）→ Gemini fallback
（google/gemini-3.1-pro-preview 优先、gemini-3.5-flash 兜底）。Gemini 走**原生视频理解**：
整条 final.mp4 以 data:video/mp4 直接入参（网关实测 image_url 部件携带 video MIME 可透传，
video_url 部件会被静默丢弃——ptok 骤降到纯文本量即被丢）；**禁止退化成抽帧**。
Gemini 能听到音轨，D5 音画协调可全维评审（Kimi 图片模式只能评画面侧）。

用法：
  python3 tools/judge/judge.py <evidence_pack_dir> --node {hero_frames|final}
      [--style-pack <name>] [--model <强制指定>] [--dry-run]
凭据（.env，worktree 缺失回退 git 主仓）：KIMI_API_KEY（kimi 用）；
GEMINI_API_KEY（gemini 用，缺省回退 MINIMAX_MUSIC_API_KEY——同网关 default 分组实测可达）；
KIMI_BASE_URL 缺省 https://new-api.neodrop.ai/v1；KIMI_MODEL 缺省 kimi-k3。
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

MAX_TOKENS = 12000       # 推理模型思考也占额度，给足否则 content 为空
MAX_SHOT_FRAMES = 10     # 逐镜帧最多送 N 张（均匀抽），contact sheet 承担全片概览
RETRIES = 2
# 网关实测（2026-07-21 二分）：2.2MB 请求过、~2.9MB 报 get_channel_failed；
# 图片数量 12 张无碍——限制在字节不在张数。预算内贪心装帧，砍掉的记进报告。
PAYLOAD_BUDGET = 2_200_000

FALLBACK_MODELS = "google/gemini-3.1-pro-preview,gemini-3.5-flash"
VIDEO_MAX_BYTES = 30_000_000   # 超此体积转低码率 proxy（仍是完整视频，不是抽帧）

RUBRIC = """D1 意图匹配 / D2 信息准确 / D3 开头吸引力 / D4 节奏 / D5 音画协调 /
D6 字幕版式 / D7 整体完成度 / D8 创意 / D9 网感。1-5 整数分。
D8 的核心考题：换个选题/产品名还成立吗（模板味测试）——成立即 ≤2。
D9 看出现在推荐页违不违和。注意你只有画面证据没有音轨，D5 只评画面侧可判部分
（字幕/大字的节奏密度与断句），并在理由里声明此局限。"""

RUBRIC_AV = """D1 意图匹配 / D2 信息准确 / D3 开头吸引力 / D4 节奏 / D5 音画协调 /
D6 字幕版式 / D7 整体完成度 / D8 创意 / D9 网感。1-5 整数分。
D8 的核心考题：换个选题/产品名还成立吗（模板味测试）——成立即 ≤2。
D9 看出现在推荐页违不违和。你收到的是完整视频（含音轨）——D5 必查字幕/通屏文字/
版式大字与口播的同步（听感差 >0.2s = 不同步 = 该维 ≤2，逐句抽查 ≥6 个点）。"""


def repo_root(start: Path) -> Path:
    p = start.resolve()
    for _ in range(6):
        if (p / "styles").is_dir():
            return p
        p = p.parent
    return start


def load_env() -> dict:
    """读 .env：优先仓库根，worktree 无 .env 回退 git 主仓。"""
    here = Path(__file__).resolve().parent.parent.parent
    candidates = [here / ".env"]
    try:
        common = subprocess.run(
            ["git", "-C", str(here), "rev-parse", "--path-format=absolute",
             "--git-common-dir"], capture_output=True, text=True).stdout.strip()
        if common:
            candidates.append(Path(common).parent / ".env")
    except OSError:
        pass
    env = {}
    for f in candidates:
        if f.is_file():
            for line in f.read_text().splitlines():
                if "=" in line and not line.lstrip().startswith("#"):
                    k, _, v = line.partition("=")
                    env.setdefault(k.strip(), v.strip())
    return env


def img_part(path: Path) -> dict:
    mime = "image/png" if path.suffix == ".png" else "image/jpeg"
    b64 = base64.b64encode(path.read_bytes()).decode()
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}


def anti_patterns(style_pack: str, pack_dir: Path) -> str:
    """从风格包 playbook 提取 §6 反模式清单原文，逐条进评委 prompt。"""
    pb = pack_dir / "playbook.md"
    if not pb.is_file():
        return "（风格包 playbook 缺失，按通用反模式：幻灯片化 / PPT 双角标 / 模板味 / 转场遮丑）"
    text = pb.read_text(encoding="utf-8")
    m = re.search(r"##[^\n]*反模式[^\n]*\n(.*?)(?=\n## |\Z)", text, re.S)
    return m.group(1).strip() if m else "（playbook 无反模式节）"


def _first(pack: Path, stem: str) -> Path:
    for ext in (".jpg", ".png"):
        if (pack / (stem + ext)).is_file():
            return pack / (stem + ext)
    return pack / (stem + ".jpg")


def _task_text(node: str, rubric: str) -> str:
    if node == "hero_frames":
        return (
            "节点：hero-frame 品味门（storyboard 之前）。上面是本片 3 张 hero frame 与 "
            "Golden contact sheet。判断：1) 每张 hero frame 是否达到 Golden 的视觉下限"
            "（质感/版式/风格兑现）；2) 风格承诺是否兑现（对照反模式清单）；"
            "3) 模板味测试。未达下限 = 打回，禁止铺开全片生产。\n"
            "输出 JSON: {\"node\":\"hero_frames\",\"verdict\":\"pass|fail\","
            "\"per_frame\":[{\"frame\":\"...\",\"pass\":bool,\"reason\":\"...(带引用)\"}],"
            "\"anti_patterns_hit\":[{\"pattern\":\"...\",\"citation\":\"...\"}],"
            "\"template_test\":\"...\",\"must_fix\":[\"...(带引用)\"]}")
    return (
        f"节点：成片门。按 9 维评分卡打分：{rubric}\n"
        "每个分数必须给一句理由并引用镜头 ID 或时间码。同时逐条核对风格包反模式清单，"
        "命中即列出（带引用）。最后回答模板味测试与『幻灯片化/PPT 味』专项。\n"
        "输出 JSON: {\"node\":\"final\",\"scores\":{\"D1\":int,...,\"D9\":int},"
        "\"score_reasons\":{\"D1\":\"...(带引用)\",...},"
        "\"anti_patterns_hit\":[{\"pattern\":\"...\",\"citation\":\"...\"}],"
        "\"slides_ppt_check\":\"...(带引用)\",\"template_test\":\"...\","
        "\"verdict\":\"pass|pass_with_notes|fail\",\"must_fix\":[\"...(带引用)\"]}")


def _pack_context(pack: Path, style_pack: str, root: Path):
    """manifest + 风格包反模式 + L0 节选——两种证据模式共用的上下文。"""
    manifest = json.loads((pack / "manifest.json").read_text(encoding="utf-8"))
    pack_name = style_pack or (manifest.get("style_pack") or "")
    styles_dir = root / "styles"
    pack_dir = None
    if styles_dir.is_dir():
        hits = [d for d in styles_dir.iterdir() if d.is_dir() and d.name in pack_name]
        pack_dir = max(hits, key=lambda d: len(d.name)) if hits else None
    ap_text = anti_patterns(pack_name, pack_dir) if pack_dir else "（未识别风格包）"
    l0 = ""
    l0f = pack / "l0-report.json"
    if l0f.is_file():
        l0 = l0f.read_text(encoding="utf-8")[:4000]
    header = (
        f"片名：{manifest.get('title')}；风格包：{pack_name}；"
        f"画幅 {manifest.get('aspect')}；时长 {manifest.get('duration_s'):.1f}s。\n"
        f"镜头表（id/区间/意图/景别/来源）：{json.dumps(manifest.get('shots', []), ensure_ascii=False)}\n"
        f"合同带宽内调整（若有，评审时须知悉）：{json.dumps(manifest.get('contract_amendments') or {}, ensure_ascii=False)}\n"
        f"L0 仪器报告节选：{l0}\n"
        f"风格包反模式清单（一票否决，逐条核）：\n{ap_text}")
    return manifest, pack_name, header


JUDGE_SYSTEM = (
    "你是 Kuleshov 视频生产链路的独立评委（G2）。你与创作者物理隔离，"
    "只看作品证据，不接受任何创作过程解释。纪律：每一条判断（扣分/反模式命中/打回理由）"
    "都必须引用具体镜头 ID（如 s03b）或时间码（如 00:42 / 42.5s），无引用的判断无效。"
    "你的职责是替用户把关品味，宁可错杀不可放水——发现幻灯片化、模板味、PPT 味时直接判。"
    "只输出一个 JSON 对象，不要输出其他文字。")


def _judge_video(pack: Path, manifest: dict) -> Path:
    """定位评审视频；超体积转低码率 proxy（完整视频，非抽帧）。"""
    video = Path(manifest.get("video_file") or "")
    if not video.is_file():
        raise FileNotFoundError(f"manifest.video_file 不存在: {video}（重跑 build_evidence_pack）")
    if video.stat().st_size <= VIDEO_MAX_BYTES:
        return video
    proxy = pack / "video-proxy.mp4"
    if not proxy.is_file():
        subprocess.run(
            ["/opt/homebrew/bin/ffmpeg", "-y", "-loglevel", "error", "-i", str(video),
             "-vf", "scale='min(720,iw)':-2", "-c:v", "libx264", "-crf", "30",
             "-preset", "fast", "-c:a", "aac", "-b:a", "96k", str(proxy)], check=True)
    return proxy


def _build_messages_video(pack: Path, node: str, style_pack: str, root: Path):
    """Gemini 原生视频证据模式（final 节点专用；hero_frames 仍走图片模式）。"""
    manifest, pack_name, header = _pack_context(pack, style_pack, root)
    video = _judge_video(pack, manifest)
    b64 = base64.b64encode(video.read_bytes()).decode()
    parts = [
        {"type": "text", "text": "【完整成片视频（含音轨）】"},
        {"type": "image_url", "image_url": {"url": f"data:video/mp4;base64,{b64}"}},
    ]
    imgs_meta = [f"完整成片视频 {video.name}（{video.stat().st_size // 1024}KB）"]
    g = _first(pack, "golden-contact-sheet")
    if g.is_file():
        parts.append({"type": "text", "text":
                      f"【图片: Golden 样片 contact sheet（{manifest.get('golden')}，"
                      "同风格包已验收基准——风格并排对照）】"})
        parts.append(img_part(g))
        imgs_meta.append("golden contact sheet")
    parts.append({"type": "text",
                  "text": f"{header}\n\n{_task_text(node, RUBRIC_AV)}"})
    return [{"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": parts}], imgs_meta, []


def _build_messages(pack: Path, node: str, style_pack: str, root: Path):
    """图片证据模式（kimi 等无原生视频的模型）。"""
    manifest, pack_name, header = _pack_context(pack, style_pack, root)
    parts: list[dict] = []
    imgs_meta: list[str] = []
    imgs_dropped: list[str] = []
    budget = [PAYLOAD_BUDGET]

    def add_img(p: Path, label: str, must: bool = False):
        if not p.is_file():
            return
        part = img_part(p)
        cost = len(part["image_url"]["url"])
        if not must and cost > budget[0]:
            imgs_dropped.append(label)
            return
        budget[0] -= cost
        parts.append({"type": "text", "text": f"【图片: {label}】"})
        parts.append(part)
        imgs_meta.append(label)

    gtm = manifest.get("grid_time_map") or {"cols": 8, "interval_s": 2.0}
    grid_note = (f"（行优先 {gtm['cols']} 列，第 n 格时间 = (n-1)×{gtm['interval_s']:g}s；"
                 "引用时按此换算出时间码）")
    add_img(_first(pack, "contact-sheet"), f"本片 contact sheet {grid_note}", must=True)
    add_img(_first(pack, "contact-sheet-offset"),
            f"本片 contact sheet 半步错位版（同上但整体 +{gtm['interval_s']/2:g}s）", must=True)
    add_img(_first(pack, "golden-contact-sheet"),
            f"Golden 样片 contact sheet（{manifest.get('golden')}，同风格包的已验收基准——并排对照）")

    frames_dir = pack / "frames"
    frame_files = sorted(frames_dir.glob("*.jpg")) if frames_dir.is_dir() else []
    if node == "hero_frames":
        for f in frame_files:  # hero 门就 3 张，全送
            add_img(f, f"hero frame: {f.stem}")
    else:
        step = max(1, len(frame_files) // MAX_SHOT_FRAMES)
        for f in frame_files[::step][:MAX_SHOT_FRAMES]:
            add_img(f, f"镜头帧: {f.stem}")

    parts.append({"type": "text", "text": f"{header}\n\n{_task_text(node, RUBRIC)}"})
    if imgs_dropped:
        parts.append({"type": "text", "text":
                      f"（负载预算内未随附 {len(imgs_dropped)} 张逐镜帧：{'、'.join(imgs_dropped)}——"
                      "以 contact sheet 为准评审这些区间）"})
    return [{"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": parts}], imgs_meta, imgs_dropped


CITE_RE = re.compile(r"\bs\d{1,3}[a-z_]*\b|\d{1,2}:\d{2}|\d{1,3}(\.\d+)?s\b")
# D9 网感是整体维度——评分卡口径其锚点是标题/钩子/推荐页语境，不强求镜头 ID
HOLISTIC_ANCHOR_RE = re.compile(r"钩子|标题|开场|推荐页|推荐流|封面")


def validate_citations(report: dict) -> dict:
    """无镜头 ID/时间码引用的判断标 invalid（隔离评委的核心纪律）。"""
    invalid = []
    def check(label: str, text, holistic=False):
        if not isinstance(text, str) or not text.strip():
            return
        if CITE_RE.search(text) or (holistic and HOLISTIC_ANCHOR_RE.search(text)):
            return
        invalid.append(label)
    for k, r in (report.get("score_reasons") or {}).items():
        check(f"score_reasons.{k}", r, holistic=(k == "D9"))
    for i, hit in enumerate(report.get("anti_patterns_hit") or []):
        check(f"anti_patterns_hit[{i}]", (hit or {}).get("citation", ""))
    for i, m in enumerate(report.get("must_fix") or []):
        check(f"must_fix[{i}]", m)
    for i, f in enumerate(report.get("per_frame") or []):
        check(f"per_frame[{i}]", (f or {}).get("reason", ""))
    report["citations_valid"] = not invalid
    report["citations_invalid_items"] = invalid
    return report


def call_model(messages: list[dict], env: dict, model: str, api_key: str) -> dict:
    payload = {"model": model, "messages": messages,
               "max_tokens": MAX_TOKENS, "temperature": 0.3,
               "response_format": {"type": "json_object"}}
    base = env.get("KIMI_BASE_URL", "https://new-api.neodrop.ai/v1").rstrip("/")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(payload, f, ensure_ascii=False)
        req_file = f.name
    last_err = None
    for attempt in range(RETRIES + 1):
        r = subprocess.run(
            ["curl", "-sS", "-m", "600", f"{base}/chat/completions",
             "-H", f"Authorization: Bearer {api_key}",
             "-H", "Content-Type: application/json", "-d", f"@{req_file}"],
            capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
            content = d["choices"][0]["message"].get("content") or ""
            if not content.strip():
                raise ValueError(f"content 为空（reasoning 吃满额度？usage={d.get('usage')}）")
            m = re.search(r"\{.*\}", content, re.S)
            report = json.loads(m.group(0) if m else content)
            report["_usage"] = d.get("usage")
            return report
        except Exception as e:  # noqa: BLE001 —— 网络/解析失败统一重试，最终如实抛出
            last_err = f"{type(e).__name__}: {e} | resp[:300]={r.stdout[:300]!r}"
    raise RuntimeError(f"评委调用失败（重试 {RETRIES} 次后）：{last_err}")


def _key_for(model: str, env: dict) -> str | None:
    if "gemini" in model.lower():
        return env.get("GEMINI_API_KEY") or env.get("MINIMAX_MUSIC_API_KEY")
    return env.get("KIMI_API_KEY")


def _mode_for(model: str, node: str) -> str:
    # Gemini 原生视频只在成片门有意义；hero_frames 没有成片，仍走图片证据
    return "native_video" if "gemini" in model.lower() and node == "final" else "images"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack")
    ap.add_argument("--node", required=True, choices=["hero_frames", "final"])
    ap.add_argument("--style-pack", default="")
    ap.add_argument("--model", default="",
                    help="强制指定模型（跳过 fallback 链）")
    ap.add_argument("--dry-run", action="store_true",
                    help="打印模型链与将发送的消息结构，不调网络")
    args = ap.parse_args()

    pack = Path(args.pack)
    root = repo_root(pack)
    env = load_env()
    chain = ([args.model] if args.model else
             [env.get("KIMI_MODEL", "kimi-k3")] +
             (env.get("JUDGE_FALLBACK_MODELS") or FALLBACK_MODELS).split(","))
    chain = [m.strip() for m in chain if m.strip()]

    built: dict[str, tuple] = {}   # 证据模式 → (messages, imgs, dropped)

    def build(mode: str):
        if mode not in built:
            built[mode] = (_build_messages_video(pack, args.node, args.style_pack, root)
                           if mode == "native_video"
                           else _build_messages(pack, args.node, args.style_pack, root))
        return built[mode]

    if args.dry_run:
        plan = []
        for m in chain:
            mode = _mode_for(m, args.node)
            _, imgs, dropped = build(mode)
            plan.append({"model": m, "mode": mode, "evidence": imgs,
                         "dropped": dropped,
                         "key": "ready" if _key_for(m, env) else "missing"})
        print(json.dumps({"dry_run": True, "node": args.node, "chain": plan},
                         ensure_ascii=False, indent=2))
        return 0

    report, used_model, trace = None, None, []
    for m in chain:
        key = _key_for(m, env)
        if not key:
            trace.append({"model": m, "error": "缺凭据"})
            continue
        mode = _mode_for(m, args.node)
        try:
            messages, imgs, dropped = build(mode)
            report = call_model(messages, env, m, key)
            used_model, used_mode = m, mode
            break
        except Exception as e:  # noqa: BLE001 —— 逐模型 fallback，全链失败才抛
            trace.append({"model": m, "error": str(e)[:300]})
    if report is None:
        print(json.dumps({"ok": False, "error": "评委全链失败", "trace": trace},
                         ensure_ascii=False, indent=2), file=sys.stderr)
        return 3

    report = validate_citations(report)
    report["_judged_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    report["_model"] = used_model
    report["_evidence_mode"] = used_mode
    report["_fallback_trace"] = trace
    report["_images_sent"] = built[used_mode][1]
    report["_images_dropped"] = built[used_mode][2]
    out = pack / f"judge-report-{args.node}.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": True, "report": str(out),
                      "model": used_model, "mode": used_mode,
                      "verdict": report.get("verdict"),
                      "scores": report.get("scores"),
                      "citations_valid": report.get("citations_valid")},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
