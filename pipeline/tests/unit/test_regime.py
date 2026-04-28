"""Regime model determinism + label ordering."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np

from vlens.regime.changepoint import changepoint_regime, detect_changepoints
from vlens.regime.hmm import LookaheadError, fit_predict_hmm


def _toy_features(n: int = 120, seed: int = 0) -> tuple[list[date], np.ndarray]:
    g = np.random.default_rng(seed)
    half = n // 2
    rv = np.concatenate([g.normal(0.10, 0.01, half), g.normal(0.30, 0.02, n - half)])
    iv_minus_rv = g.normal(0.0, 0.005, n)
    rr = g.normal(0.0, 0.005, n)
    slope = g.normal(0.0, 0.005, n)
    feats = np.stack([rv, iv_minus_rv, rr, slope], axis=1)
    dates = [date(2024, 1, 1) + timedelta(days=i) for i in range(n)]
    return dates, feats


def test_hmm_is_deterministic_under_seed() -> None:
    d, x = _toy_features()
    a = fit_predict_hmm(symbol="X", dates=d, features=x, n_states=2, seed=7)
    b = fit_predict_hmm(symbol="X", dates=d, features=x, n_states=2, seed=7)
    assert [r.state for r in a.states] == [r.state for r in b.states]


def test_hmm_labels_calm_then_stress_in_order() -> None:
    d, x = _toy_features()
    snap = fit_predict_hmm(symbol="X", dates=d, features=x, n_states=2, seed=0)
    # Calm rank 0, stress rank 1 — first half should mostly be 0, last half mostly 1.
    states = np.array([r.state for r in snap.states])
    assert states[:60].mean() < states[60:].mean()
    assert snap.state_labels["0"] == "calm"
    assert snap.state_labels["1"] == "stress"


def test_hmm_cutoff_before_first_obs_raises() -> None:
    d, x = _toy_features()
    try:
        fit_predict_hmm(
            symbol="X", dates=d, features=x, n_states=2, seed=0, cutoff=date(2023, 1, 1)
        )
    except LookaheadError:
        return
    raise AssertionError("expected LookaheadError")


def test_changepoint_segments_simple_step() -> None:
    x = np.concatenate([np.zeros(50), np.ones(50) * 5.0])
    cps = detect_changepoints(x, penalty=2.0)
    assert any(45 <= c <= 55 for c in cps)


def test_changepoint_regime_returns_snapshot() -> None:
    d, x = _toy_features(n=80)
    snap = changepoint_regime(symbol="X", dates=d, features=x, seed=0, penalty=3.0)
    assert snap.model == "changepoint_pelt"
    assert len(snap.states) == len(d)
