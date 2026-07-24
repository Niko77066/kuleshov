"""风格合同门（style.contract.*）：P0-2 的回归考卷。

场景取自 2026-07-20 五片对照实验的真实病灶：
- Codex hf-breach：case-file 三声部压成单声部（collage=0）、成片 0 个 <video>、静态持有 75%、
  13 镜 static_class 全误标 false；
- Codex ac-26c：pixel-chronicle 像素叙事 0%（16 MG + 8 实拍）、五连 MG ≈36s。
"""

import json

import pytest

from film_ir.contract import load_contract
from film_ir.gates import run_gates
from film_ir.models import FilmIR

from conftest import minimal_ir, shot


CASE_FILE_CONTRACT = {
    "schema": "style-contract@1",
    "style_pack": "case-file",
    "plan": {
        "voices": {
            "collage_broll": {"providers": ["collage_broll"],
                              "min_shots": {"value": 3, "amend": [2, 6]}},
            "document": {"providers": ["hyperframes"], "declared_as": "document",
                         "min_shots": {"value": 1, "amend": [1, 4]}},
        },
    },
    "render": {
        "static_hold_ratio_max": {"value": 0.6, "amend": [0.45, 0.65]},
        "min_video_elements": {"value": 3, "amend": [2, 99]},
    },
}

PIXEL_CONTRACT = {
    "schema": "style-contract@1",
    "style_pack": "pixel-chronicle",
    "plan": {
        "traits": {
            "pixel_narrative": {"share_min": {"value": 0.4, "amend": [0.3, 0.5]}},
        },
        "graphics_run_max_s": {"value": 26, "amend": [22, 34]},
    },
}

MEME_CONTRACT = {
    "schema": "style-contract@1",
    "style_pack": "meme-ledger",
    "plan": {
        "voices": {
            "licensed_channel_footage": {
                "providers": ["footage"],
                "min_shots": {"value": 2, "amend": [2, 99]},
            },
        },
        "provider_share": {
            "footage": {
                "min": {"value": 1, "amend": [1, 1]},
                "max": {"value": 1, "amend": [1, 1]},
            },
        },
        "footage_source": {
            "provider": "footage",
            "channel_url": "https://www.youtube.com/@UnusualVideos",
            "required_params": ["channel_url", "source_url", "video_id", "in_s", "out_s", "license_ref"],
        },
    },
    "audio": {
        "voiceover": {
            "model": "speech-2.8-hd",
            "voice_profile_suffix": "meme-ledger/voice-profile.json",
            "required_fields": ["voice_profile", "authorization_ref"],
        },
        "music": {
            "required": True,
            "selection_method": "seeded_uniform_random",
            "instrumental_required": True,
            "loop_required": True,
            "required_fields": ["file", "track_id", "selection_seed", "license_ref"],
        },
    },
    "compose": {
        "no_effects": True,
        "allowed_overlay_types": ["caption", "subtitle"],
        "caption_terminal_punctuation": "forbidden",
        "forbidden_source_params": ["effects", "animation", "filter", "lut", "grain", "zoom", "pan"],
    },
}


@pytest.fixture
def project(tmp_path):
    """tmp 仓库骨架：<repo>/styles/<pack>/contract.json + <repo>/projects/p/。"""
    def _make(contract: dict, ir_dict: dict, evidence: dict | None = None):
        pack = contract["style_pack"]
        pack_dir = tmp_path / "styles" / pack
        pack_dir.mkdir(parents=True)
        (pack_dir / "contract.json").write_text(
            json.dumps(contract, ensure_ascii=False), encoding="utf-8")
        pdir = tmp_path / "projects" / "p"
        pdir.mkdir(parents=True)
        if evidence is not None:
            (pdir / "evidence").mkdir()
            (pdir / "evidence" / "render-metrics.json").write_text(
                json.dumps(evidence, ensure_ascii=False), encoding="utf-8")
        return FilmIR.model_validate(ir_dict), pdir
    return _make


def _codex_hf_ir(status="storyboard", **meta_over) -> dict:
    """全 hyperframes 单声部片（Codex hf-breach 形）。"""
    ir = minimal_ir(style_pack="case-file", status=status, **meta_over)
    ir["audio"] = {"timeline": {"duration_s": 72.0, "sections": []}}
    n, seg = 12, 6.0
    ir["shots"] = [shot(f"s{i:02d}", i * seg, (i + 1) * seg,
                        provider="hyperframes", static_class=False)
                   for i in range(n)]
    ir["meta"]["commitment"]["duration_s"] = 72.0
    return ir


def _errors(report, gate):
    return [x for x in report["violations"]
            if x["gate"] == gate and x["severity"] == "error"]


def test_candidate_prefix_explicitly_loads_disabled_pack(tmp_path):
    pack_dir = tmp_path / "styles" / "_disabled" / "meme-ledger"
    pack_dir.mkdir(parents=True)
    (pack_dir / "contract.json").write_text(
        json.dumps(MEME_CONTRACT, ensure_ascii=False), encoding="utf-8")
    pdir = tmp_path / "projects" / "p"
    pdir.mkdir(parents=True)

    assert load_contract("candidate:meme-ledger", pdir) == MEME_CONTRACT
    assert load_contract("meme-ledger", pdir) is None


# ---------------------------------------------------------------- plan 门

def test_missing_voice_is_error(project):
    ir, pdir = project(CASE_FILE_CONTRACT, _codex_hf_ir())
    report = run_gates(ir, project_dir=pdir)
    msgs = [x["message"] for x in _errors(report, "style.contract.plan")]
    assert any("collage_broll" in m for m in msgs)


def test_voices_satisfied_passes(project):
    ir_dict = _codex_hf_ir()
    for i in (2, 5, 8):
        ir_dict["shots"][i]["source"] = {"provider": "collage_broll"}
    # document 声部声明在场
    ir_dict["shots"][0]["source"]["params"] = {"voice": "document"}
    ir, pdir = project(CASE_FILE_CONTRACT, ir_dict)
    report = run_gates(ir, project_dir=pdir)
    assert not _errors(report, "style.contract.plan")


def test_declared_voice_missing_is_warn_when_undeclared(project):
    """legacy 片全无 voice 声明：document 在场性降 warn，不误伤。"""
    ir_dict = _codex_hf_ir()
    for i in (2, 5, 8):
        ir_dict["shots"][i]["source"] = {"provider": "collage_broll"}
    ir, pdir = project(CASE_FILE_CONTRACT, ir_dict)
    report = run_gates(ir, project_dir=pdir)
    assert not _errors(report, "style.contract.plan")
    assert any(x["gate"] == "style.contract.plan" and "document" in x["message"]
               for x in report["violations"] if x["severity"] == "warn")


def test_amendment_within_bounds(project):
    """带宽内调整生效（3→2），端到端不断；产生可见性 warn。"""
    ir_dict = _codex_hf_ir()
    for i in (2, 5):
        ir_dict["shots"][i]["source"] = {"provider": "collage_broll"}
    ir_dict["meta"]["contract_amendments"] = {
        "plan.voices.collage_broll.min_shots": 2}
    ir, pdir = project(CASE_FILE_CONTRACT, ir_dict)
    report = run_gates(ir, project_dir=pdir)
    assert not _errors(report, "style.contract.plan")
    assert any(x["gate"] == "style.contract.amend" and x["severity"] == "warn"
               for x in report["violations"])


def test_amendment_out_of_bounds_is_violation(project):
    """越界修改（min_shots→0，等于删声部）：修改无效 + 违约双 error。"""
    ir_dict = _codex_hf_ir()
    ir_dict["meta"]["contract_amendments"] = {
        "plan.voices.collage_broll.min_shots": 0}
    ir, pdir = project(CASE_FILE_CONTRACT, ir_dict)
    report = run_gates(ir, project_dir=pdir)
    assert _errors(report, "style.contract.amend")
    assert _errors(report, "style.contract.plan")


def test_unknown_amendment_key_is_error(project):
    ir_dict = _codex_hf_ir()
    ir_dict["meta"]["contract_amendments"] = {"plan.nonexistent": 1}
    ir, pdir = project(CASE_FILE_CONTRACT, ir_dict)
    report = run_gates(ir, project_dir=pdir)
    assert _errors(report, "style.contract.amend")


def test_pixel_narrative_zero_is_error(project):
    """Codex ac-26c 形：0 个 seedance 镜、无 pixel_narrative 标记 → 像素叙事 0%。"""
    ir_dict = minimal_ir(style_pack="pixel-chronicle", status="storyboard")
    ir_dict["audio"] = {"timeline": {"duration_s": 100.0, "sections": []}}
    ir_dict["shots"] = [shot(f"s{i:02d}", i * 10.0, (i + 1) * 10.0,
                             provider="hyperframes" if i % 2 else "footage",
                             static_class=bool(i % 2))
                        for i in range(10)]
    ir, pdir = project(PIXEL_CONTRACT, ir_dict)
    report = run_gates(ir, project_dir=pdir)
    msgs = [x["message"] for x in _errors(report, "style.contract.plan")]
    assert any("像素叙事" in m for m in msgs)


def test_seedance_counts_as_pixel_narrative_fallback(project):
    ir_dict = minimal_ir(style_pack="pixel-chronicle", status="storyboard")
    ir_dict["audio"] = {"timeline": {"duration_s": 100.0, "sections": []}}
    ir_dict["shots"] = [
        shot("s01", 0, 45, provider="seedance", static_class=False,
             motion="推近"),
        shot("s02", 45, 100, provider="footage", static_class=False),
    ]
    ir, pdir = project(PIXEL_CONTRACT, ir_dict)
    ir.shot_groups = []
    report = run_gates(ir, project_dir=pdir)
    assert not any("像素叙事" in x["message"]
                   for x in _errors(report, "style.contract.plan"))


def test_graphics_run_over_limit(project):
    """五连 MG 36s（Codex ac-26c s14–s18 形）> 26s 上限。"""
    ir_dict = minimal_ir(style_pack="pixel-chronicle", status="storyboard")
    ir_dict["audio"] = {"timeline": {"duration_s": 72.0, "sections": []}}
    shots = [shot("s00", 0, 18, provider="seedance", static_class=False,
                  source={"provider": "seedance",
                          "params": {"pixel_narrative": True}}),
             shot("s0x", 18, 36, provider="footage", static_class=False)]
    shots += [shot(f"s{i:02d}", 36 + (i - 1) * 7.2, 36 + i * 7.2,
                   provider="hyperframes") for i in range(1, 6)]
    ir_dict["shots"] = shots
    ir, pdir = project(PIXEL_CONTRACT, ir_dict)
    report = run_gates(ir, project_dir=pdir)
    msgs = [x["message"] for x in _errors(report, "style.contract.plan")]
    assert any("连续" in m for m in msgs)


def _meme_ir(status="storyboard") -> dict:
    ir = minimal_ir(style_pack="meme-ledger", status=status)
    ir["meta"]["commitment"]["duration_s"] = 10
    ir["audio"] = {
        "timeline": {"duration_s": 10, "sections": []},
        "voiceover": {
            "voice_profile": "styles/_disabled/meme-ledger/voice-profile.json",
            "authorization_ref": "rights/voice-authorized.md",
            "gen": {"model": "speech-2.8-hd (delegated)"},
        },
        "music": {
            "file": "audio/bgm.mp3", "track_id": "awaken",
            "selection_method": "seeded_uniform_random", "selection_seed": 17,
            "instrumental": True, "loop": True,
            "license_ref": "rights/bgm-awaken.pdf",
        },
    }
    params = {
        "channel_url": "https://www.youtube.com/@UnusualVideos",
        "source_url": "https://www.youtube.com/watch?v=abc",
        "video_id": "abc", "in_s": 1.2, "out_s": 5.8,
        "license_ref": "rights/unusual-videos-collab.pdf",
    }
    ir["shots"] = [
        shot("s01", 0, 5, provider="footage", source={"provider": "footage", "params": params}),
        shot("s02", 5, 10, provider="footage", source={"provider": "footage", "params": params}),
    ]
    return ir


def test_meme_contract_passes_with_traced_source_audio_and_plain_compose(project):
    ir, pdir = project(MEME_CONTRACT, _meme_ir(status="compose"))
    report = run_gates(ir, project_dir=pdir)
    assert not [x for x in report["violations"]
                if x["severity"] == "error" and x["gate"].startswith("style.contract")]


def test_meme_contract_rejects_wrong_channel_and_missing_timecode(project):
    ir_dict = _meme_ir()
    params = ir_dict["shots"][0]["source"]["params"]
    params["channel_url"] = "https://www.youtube.com/@Other"
    params.pop("out_s")
    ir, pdir = project(MEME_CONTRACT, ir_dict)
    report = run_gates(ir, project_dir=pdir)
    msgs = [x["message"] for x in _errors(report, "style.contract.plan")]
    assert any("out_s" in m for m in msgs)
    assert any("频道" in m for m in msgs)


def test_meme_contract_rejects_incomplete_or_unlicensed_bgm(project):
    ir_dict = _meme_ir(status="audio")
    ir_dict["audio"]["music"].update({
        "track_id": "", "instrumental": False, "loop": False,
        "license_ref": "",
    })
    ir, pdir = project(MEME_CONTRACT, ir_dict)
    report = run_gates(ir, project_dir=pdir)
    msgs = [x["message"] for x in _errors(report, "style.contract.audio")]
    assert any("track_id" in m for m in msgs)
    assert any("纯器乐" in m for m in msgs)
    assert any("循环" in m for m in msgs)
    assert any("license_ref" in m for m in msgs)


def test_meme_contract_rejects_hyperframes_effects(project):
    ir_dict = _meme_ir(status="compose")
    ir_dict["edit"].update({"transitions": ["crossfade"], "lut": "warm.cube", "grain": "8%"})
    ir_dict["shots"][0]["source"]["params"]["zoom"] = 1.1
    ir_dict["overlays"] = [{"id": "o1", "type": "thesis_card", "scope": "global"}]
    ir, pdir = project(MEME_CONTRACT, ir_dict)
    report = run_gates(ir, project_dir=pdir)
    msgs = [x["message"] for x in _errors(report, "style.contract.compose")]
    assert any("转场" in m for m in msgs)
    assert any("LUT" in m for m in msgs)
    assert any("颗粒" in m for m in msgs)
    assert any("zoom" in m for m in msgs)
    assert any("叠加层" in m for m in msgs)


def test_meme_contract_rejects_caption_terminal_punctuation(project):
    ir_dict = _meme_ir(status="compose")
    ir_dict["overlays"] = [{
        "id": "o1", "type": "caption", "text": "银行还在旁边抱着计算器。",
    }]
    ir, pdir = project(MEME_CONTRACT, ir_dict)
    report = run_gates(ir, project_dir=pdir)
    msgs = [x["message"] for x in _errors(report, "style.contract.compose")]
    assert any("句末不得添加标点" in m for m in msgs)


# ---------------------------------------------------------------- render 门

def _evidence(hold_ratio=0.75, video_elements=0, per_shot=None) -> dict:
    return {
        "schema": "render-metrics@1",
        "video": {"duration_s": 72.0},
        "static": {"hold_ratio": hold_ratio, "hold_total_s": hold_ratio * 72,
                   "per_shot": per_shot or []},
        "compose": {"video_elements": video_elements},
    }


def test_render_evidence_missing_is_error_in_review(project):
    ir, pdir = project(CASE_FILE_CONTRACT, _codex_hf_ir(status="review"))
    report = run_gates(ir, project_dir=pdir)
    assert _errors(report, "style.contract.render")


def test_render_codex_shape_fails(project):
    """静态持有 75% + 0 个 <video> + 12 镜自报/实测矛盾 → 三重 error。"""
    per_shot = [{"id": f"s{i:02d}", "measured_static": True} for i in range(12)]
    ir, pdir = project(CASE_FILE_CONTRACT, _codex_hf_ir(status="review"),
                       evidence=_evidence(0.75, 0, per_shot))
    report = run_gates(ir, project_dir=pdir)
    msgs = [x["message"] for x in _errors(report, "style.contract.render")]
    assert any("静态持有" in m for m in msgs)
    assert any("<video>" in m for m in msgs)
    assert any("static_class" in m for m in msgs)


def test_render_polished_shape_passes(project):
    """打磨版形：52% 持有 + 4 个 <video> → render 门无 error。"""
    ir, pdir = project(CASE_FILE_CONTRACT, _codex_hf_ir(status="review"),
                       evidence=_evidence(0.52, 4))
    report = run_gates(ir, project_dir=pdir)
    assert not _errors(report, "style.contract.render")


def test_no_contract_pack_skips(project, tmp_path):
    """无合同的风格包不受此门约束。"""
    ir_dict = _codex_hf_ir()
    ir_dict["meta"]["style_pack"] = "daily-brief"
    ir, pdir = project(CASE_FILE_CONTRACT, ir_dict)
    report = run_gates(ir, project_dir=pdir)
    assert not [x for x in report["violations"]
                if x["gate"].startswith("style.contract")]
