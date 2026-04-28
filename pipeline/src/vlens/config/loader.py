"""YAML loader for run configs."""

from __future__ import annotations

from pathlib import Path

import yaml

from .schema import RunConfig


def load_config(path: str | Path) -> RunConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return RunConfig.model_validate(raw)
