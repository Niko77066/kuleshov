"""M2/M3 provider 占位：注册即声明接口，调用即如实拒绝（不造假产物）。"""

from __future__ import annotations

from pathlib import Path

from ..errors import IRError, NOT_IMPLEMENTED
from ..models import FilmIR
from .base import Adapter, Plan, RunResult, Target


class _Stub(Adapter):
    milestone = ""

    def plan(self, ir: FilmIR, target: Target, project_dir: Path) -> Plan:
        raise IRError(NOT_IMPLEMENTED,
                      f"provider {self.name!r} {self.milestone} 接入（蓝图 §12），接口已就位",
                      hint="M1 期间该来源按 /produce SOP 手工生成后用 ir_patch 回填留痕")

    def run(self, ir: FilmIR, target: Target, plan: Plan, project_dir: Path) -> RunResult:
        raise IRError(NOT_IMPLEMENTED, f"provider {self.name!r} 未接入")


class SeedanceAdapter(_Stub):
    name, mode, milestone = "seedance", "baked", "M2"


class ImageMotionAdapter(_Stub):
    name, mode, milestone = "image_motion", "declarative", "M2"


class AvatarAdapter(_Stub):
    name, mode, milestone = "avatar", "baked", "M2"


class FootageAdapter(_Stub):
    name, mode, milestone = "footage", "baked", "M3（素材语料库未建）"
