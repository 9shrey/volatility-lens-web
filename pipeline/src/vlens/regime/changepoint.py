"""Change-point baseline (PELT) — pure-numpy fallback if ``ruptures`` absent."""

from __future__ import annotations

from datetime import date

import numpy as np

from ..data.schemas import RegimeSnapshot, RegimeStateRow


def detect_changepoints(x: np.ndarray, penalty: float = 5.0) -> list[int]:
    """A small PELT-style change-point detector on 1-D mean shifts.

    Returns the indices that *start* a new segment (excluding 0).
    """
    if x.ndim != 1:
        x = x.mean(axis=1)
    n = len(x)
    if n < 4:
        return []
    cum = np.concatenate([[0.0], np.cumsum(x)])
    cum_sq = np.concatenate([[0.0], np.cumsum(x**2)])

    def seg_cost(i: int, j: int) -> float:
        m = j - i
        if m <= 0:
            return 0.0
        s = cum[j] - cum[i]
        s2 = cum_sq[j] - cum_sq[i]
        return float(s2 - (s * s) / m)

    f = np.full(n + 1, np.inf)
    f[0] = -penalty
    last = np.zeros(n + 1, dtype=int)
    for j in range(1, n + 1):
        for i in range(0, j):
            c = f[i] + seg_cost(i, j) + penalty
            if c < f[j]:
                f[j] = c
                last[j] = i
    cps: list[int] = []
    j = n
    while j > 0:
        i = int(last[j])
        if i > 0:
            cps.append(i)
        j = i
    return sorted(cps)


def changepoint_regime(
    *,
    symbol: str,
    dates: list[date],
    features: np.ndarray,
    seed: int,
    penalty: float = 5.0,
) -> RegimeSnapshot:
    """Convert change-points to per-day pseudo-states (segment id)."""
    cps = detect_changepoints(features.mean(axis=1) if features.ndim == 2 else features, penalty)
    seg_id = np.zeros(len(dates), dtype=int)
    cur = 0
    for i in range(len(dates)):
        if i in cps:
            cur += 1
        seg_id[i] = cur
    n_states = int(seg_id.max()) + 1
    rows = [
        RegimeStateRow(
            date=dates[i],
            state=int(seg_id[i]),
            posterior=[1.0 if k == seg_id[i] else 0.0 for k in range(n_states)],
        )
        for i in range(len(dates))
    ]
    return RegimeSnapshot(
        symbol=symbol,
        model="changepoint_pelt",
        fit_window=(dates[0], dates[-1]),
        states=rows,
        state_labels={str(k): f"segment_{k}" for k in range(n_states)},
        seed=seed,
    )
