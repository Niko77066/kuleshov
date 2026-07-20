"""三部成片（M0 三种方言）→ m1-v1 收编回归。fixtures 只读，不碰真实项目文件。"""

from film_ir.gates import run_gates
from film_ir.migrate import migrate
from film_ir.models import FilmIR, SCHEMA_VERSION

from conftest import load_fixture


def test_all_real_films_migrate_to_valid_schema(real_film_raw):
    new, log = migrate(real_film_raw)
    assert new["meta"]["schema_version"] == SCHEMA_VERSION
    assert log, "真实旧片必然有收编动作"
    ir = FilmIR.model_validate(new)
    report = run_gates(ir)          # 门套件在真实数据上必须能跑完（结果另行校准）
    assert isinstance(report["ok"], bool)


def test_migrate_idempotent(real_film_raw):
    once, _ = migrate(real_film_raw)
    twice, log2 = migrate(once)
    assert once == twice, "迁移必须幂等"


def test_800v_dialect():
    new, _ = migrate(load_fixture("800v-thermal-runaway"))
    vo = new["audio"]["voiceover"]
    assert "gen" in vo and vo["gen"]["model"], "平铺留痕收进 gen 块"
    assert "model" not in vo
    assert isinstance(new["audio"]["music"]["gen"], dict)
    assert new["meta"]["status"] == "delivered"        # delivered-v2 归一
    assert new["meta"]["status_original"] == "delivered-v2"
    for g in new["shot_groups"]:
        assert g.get("seam_out") in ("tail_relay", "hard_cut", "transition", "none", None)
    provs = {s["source"]["provider"] for s in new["shots"]}
    assert provs <= {"hyperframes", "seedance", "image_motion", "avatar", "footage", "tts"}


def test_samsung_dialect():
    new, _ = migrate(load_fixture("samsung-health-ai-consent"))
    assert any(s["source"]["provider"] == "avatar" for s in new["shots"])
    for o in new["overlays"]:
        assert "range" not in o
        assert o.get("shot_range") or o.get("shot_refs") or o.get("scope") == "global"
    # source.group → group_ref
    grouped = [s for s in new["shots"] if s.get("group_ref")]
    assert grouped, "samsung 的 source.group 应迁为 group_ref"


def test_estee_dialect():
    new, _ = migrate(load_fixture("estee-lauder-night"))
    assert all("static_type" not in s for s in new["shots"])
    ov_by_id = {o["id"]: o for o in new["overlays"]}
    assert ov_by_id["ov_sub"]["scope"] == "global"
    assert ov_by_id["ov_num_22"]["shot_range"] == ["s01_hook_film_number", "s01_hook_film_number"]
    assert ov_by_id["ov_tag_brand"]["shot_refs"] == ["s01_hook_film_number", "s06b_space_float"]
