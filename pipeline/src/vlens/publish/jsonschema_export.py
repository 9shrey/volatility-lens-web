"""Export pydantic models to JSON Schema for the TS side to codegen zod from."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..data import schemas as schema_models
from ..utils.io import write_json

_MODELS = [
    schema_models.OptionQuote,
    schema_models.IVPoint,
    schema_models.GridSpec,
    schema_models.SVIParams,
    schema_models.SurfaceQuality,
    schema_models.SurfaceSnapshot,
    schema_models.SkewMetric,
    schema_models.TermPoint,
    schema_models.RegimeStateRow,
    schema_models.RegimeSnapshot,
    schema_models.TickerIndexEntry,
    schema_models.TickerIndex,
    schema_models.Manifest,
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
