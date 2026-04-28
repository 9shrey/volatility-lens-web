"""End-to-end smoke: publish, verify manifest, and assert determinism."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from vlens.config.loader import load_config
from vlens.publish.artifacts import write_bundle
from vlens.publish.jsonschema_export import export
from vlens.publish.manifest import verify_bundle
from vlens.utils.hashing import sha256_hex
from vlens.utils.seeding import set_global_seed

CFG_PATH = Path(__file__).resolve().parents[2] / "configs" / "smoke.yaml"


def _hash_tree(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root)).replace("\\", "/"): sha256_hex(p.read_bytes())
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


@pytest.mark.timeout(120)
def test_smoke_publish_then_verify(tmp_path: Path) -> None:
    cfg = load_config(CFG_PATH)
    set_global_seed(cfg.seed)
    out = tmp_path / "bundle"
    write_bundle(out_root=out, cfg=cfg)
    assert (out / "manifest.json").exists()
    assert (out / "index.json").exists()
    assert (out / "tickers" / "SPY").is_dir()
    manifest = verify_bundle(out)
    assert manifest["schema_version"] == "1.0"


@pytest.mark.timeout(180)
def test_smoke_publish_is_deterministic(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = load_config(CFG_PATH)
    monkeypatch.setenv("VLENS_PRODUCED_AT", "2024-12-31T00:00:00+00:00")
    monkeypatch.setenv("VLENS_PIPELINE_GIT_SHA", "deadbeef")
    a = tmp_path / "a"
    b = tmp_path / "b"
    set_global_seed(cfg.seed)
    write_bundle(out_root=a, cfg=cfg)
    set_global_seed(cfg.seed)
    write_bundle(out_root=b, cfg=cfg)
    ha = _hash_tree(a)
    hb = _hash_tree(b)
    assert ha == hb, f"Bundle is not deterministic: {set(ha) ^ set(hb)}"


def test_jsonschema_export(tmp_path: Path) -> None:
    p = tmp_path / "schemas.json"
    export(p)
    bundle = json.loads(p.read_text())
    assert "definitions" in bundle
    for name in ("SurfaceSnapshot", "RegimeSnapshot", "Manifest"):
        assert name in bundle["definitions"]
