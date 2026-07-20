"""执行层：Rule Zero、占位拒绝、TTS 计划与时间轴构建、HyperFrames lint 门。"""

import json

import pytest

from film_ir.errors import IRError
from film_ir.execute import resolve_target, execute
from film_ir.execute.tts import TTSAdapter, _timeline_from_subtitle
from film_ir.execute.base import Target
from film_ir.models import FilmIR
from film_ir.store import Project

from conftest import minimal_ir, shot


@pytest.fixture
def project(tmp_path):
    d = minimal_ir(status="audio")
    d["audio"]["voiceover"] = {"text_prompt_file": "script-tts.txt"}
    d["shots"] = [shot("s01", 0.0, 5.0, provider="seedance")]
    (tmp_path / "film.json").write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    (tmp_path / "script-tts.txt").write_text(
        "一位专业的中文新闻播报员朗读：“库勒肖夫链路测试。”", encoding="utf-8")
    return Project(tmp_path)


def test_rule_zero_rejects_unknown_target(project):
    ir = project.load()
    with pytest.raises(IRError) as e:
        resolve_target(ir, "shots.s99")
    assert e.value.code == "RULE_ZERO"


def test_rule_zero_rejects_voiceover_without_entry(tmp_path):
    d = minimal_ir()
    (tmp_path / "film.json").write_text(json.dumps(d), encoding="utf-8")
    ir = Project(tmp_path).load()
    with pytest.raises(IRError) as e:
        resolve_target(ir, "audio.voiceover")
    assert e.value.code == "RULE_ZERO"


def test_stub_provider_not_implemented(project):
    with pytest.raises(IRError) as e:
        execute(project, ["shots.s01"], dry_run=True)   # s01 → seedance 占位
    assert e.value.code == "NOT_IMPLEMENTED"


def test_tts_plan(project):
    ir = project.load()
    plan = TTSAdapter().plan(ir, Target("audio.voiceover", "audio.voiceover", None, "tts"),
                             project.dir)
    payload = plan.requests[0]
    assert payload["model"] == "seed-audio-1.0"
    assert payload["audio_config"]["enable_subtitle"] is True
    assert "朗读" in payload["text_prompt"]


def test_tts_plan_missing_prompt_file(tmp_path):
    d = minimal_ir()
    d["audio"]["voiceover"] = {}
    (tmp_path / "film.json").write_text(json.dumps(d), encoding="utf-8")
    p = Project(tmp_path)
    ir = p.load()
    with pytest.raises(IRError) as e:
        TTSAdapter().plan(ir, Target("audio.voiceover", "audio.voiceover", None, "tts"), p.dir)
    assert e.value.code == "RULE_ZERO"


def test_timeline_from_subtitle_filters_punctuation():
    tl = _timeline_from_subtitle({"sentences": [{
        "start_time": 193, "end_time": 2072, "text": "测试句。",
        "words": [{"start_time": 193, "end_time": 340, "text": "测"},
                  {"start_time": 340, "end_time": 500, "text": "试"},
                  {"start_time": 500, "end_time": 900, "text": "句"},
                  {"start_time": 900, "end_time": 900, "text": "。"}],   # 零时长标点
    }]})
    assert tl["duration_s"] == 2.072
    assert tl["sections"][0]["id"] == "sec01"
    assert tl["words_count"] == 3


def test_execute_dry_run_tts(project):
    out = execute(project, ["audio.voiceover"], dry_run=True)
    assert out["results"][0]["dry_run"] is True
    assert out["results"][0]["provider"] == "tts"


def test_budget_fuse(project, monkeypatch):
    from film_ir import api
    api.ir_patch(project.dir, [
        {"op": "set", "path": "meta.budget", "value": {"cap_usd": 1.0, "spent_usd": 2.0}},
    ], revision={"reason": "测试熔断"})
    with pytest.raises(IRError) as e:
        execute(Project(project.dir), ["audio.voiceover"])
    assert "熔断" in e.value.message


def test_hyperframes_lint_gate(tmp_path, monkeypatch):
    import subprocess
    from film_ir.execute.hyperframes import HyperframesAdapter

    d = minimal_ir(status="compose")
    (tmp_path / "film.json").write_text(json.dumps(d), encoding="utf-8")
    (tmp_path / "compose").mkdir()
    p = Project(tmp_path)

    calls = []

    def fake_run(cmd, **kw):
        calls.append(cmd)
        class R:
            returncode = 1 if "lint" in cmd else 0
            stdout, stderr = "", "clip missing data-start"
        return R()

    monkeypatch.setattr(subprocess, "run", fake_run)
    ad = HyperframesAdapter()
    target = Target("compose", "compose", None, "hyperframes")
    plan = ad.plan(p.load(), target, p.dir)
    with pytest.raises(IRError) as e:
        ad.run(p.load(), target, plan, p.dir)
    assert "lint 不过" in e.value.message
    assert len(calls) == 1, "lint 不过必须禁 render"
