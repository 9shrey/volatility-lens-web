from __future__ import annotations

from pathlib import Path

from vlens.config.loader import load_config


CFG_DIR = Path(__file__).resolve().parents[2] / "configs"


def test_load_smoke_config() -> None:
    cfg = load_config(CFG_DIR / "smoke.yaml")
    assert cfg.universe.tickers == ["SPY"]
    assert cfg.data.source == "synthetic"
    assert cfg.surface.svi.bounds.b_min == 0.0


def test_load_default_config() -> None:
    cfg = load_config(CFG_DIR / "default.yaml")
    assert len(cfg.universe.tickers) >= 1
