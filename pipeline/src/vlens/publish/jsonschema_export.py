"""Export pydantic models to JSON Schema for the TS side to codegen zod from."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..data import schemas as S
from ..utils.io import write_json

_MODELS = [
    S.OptionQuote,
    S.IVPoint,
    S.GridSpec,
    S.SVIParams,
    S.SurfaceQuality,
    S.SurfaceSnapshot,
    S.SkewMetric,
    S.TermPoint,
    S.RegimeStateRow,
    S.RegimeSnapshot,
    S.TickerIndexEntry,
    S.TickerIndex,
    S.Manifest,
]


def build_schema_bundle() -> dict[str, Any]:
    out: dict[str, Any] = {"$schema": "http://json-schema.org/draft-07/schema#", "definitions": {}}
    for m in _MODELS:
        out["definitions"][m.__name__] = m.model_json_schema()
    return out


def export(out_path: Path) -> Path:
    bundle = build_schema_bundle()
    write_json(out_path, bundle)
    return out_path
