"""Synthetic SVI-based option-chain & price-history generator.

Used by the smoke + default configs so the entire pipeline runs end-to-end
on CPU, deterministically, with no API keys required.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np

from ..utils.seeding import rng

# Business-day calendar (5/7) is sufficient for the synthetic path.


def business_days(start: date, end: date) -> list[date]:
    out: list[date] = []
    d = start
    one = timedelta(days=1)
    while d <= end:
        if d.weekday() < 5:
            out.append(d)
        d = d + one
    return out


@dataclass(frozen=True)
class SyntheticParams:
    """Time-varying SVI base parameters."""

    a0: float = 0.02
    b0: float = 0.10
    rho0: float = -0.30
    m0: float = 0.0
    sigma0: float = 0.20

    # regime modulation
    stress_drift: float = 0.04        # bumps `a` during stress
    stress_skew: float = -0.20        # bumps `rho` during stress


def svi_total_variance(
    k: np.ndarray,
    a: float,
    b: float,
    rho: float,
    m: float,
    sigma: float,
) -> np.ndarray:
    """Raw SVI total variance w(k)."""
    return a + b * (rho * (k - m) + np.sqrt((k - m) ** 2 + sigma**2))


def svi_iv(k: np.ndarray, t_years: float, **svi: float) -> np.ndarray:
    """Implied vol from total variance: sigma_iv = sqrt(w/t)."""
    w = svi_total_variance(k, **svi)
    w = np.clip(w, 1e-8, None)
    return np.sqrt(w / max(t_years, 1e-6))


@dataclass
class SyntheticPath:
    dates: list[date]
    underlying: np.ndarray            # shape [T]
    realized_vol_21d: np.ndarray      # shape [T]
    regime: np.ndarray                # shape [T] in {0,1,2}
    surfaces: list[np.ndarray]        # each: [n_tenor, n_moneyness]
    svi_params: list[dict[float, dict[str, float]]]   # per date, tenor -> params
    moneyness_grid: np.ndarray
    tenor_grid_years: np.ndarray


def generate_path(
    symbol: str,
    start: date,
    end: date,
    moneyness_grid: list[float],
    tenor_grid_days: list[int],
    seed: int,
    params: SyntheticParams = SyntheticParams(),
) -> SyntheticPath:
    """Generate a deterministic price path + SVI surface time series.

    The regime is a 3-state Markov chain whose state shifts the SVI base level
    and skew, producing recognizable patterns for the regime model to recover.
    """
    g = rng(seed)
    dates = business_days(start, end)
    t = len(dates)

    # 3-state Markov chain (calm / normal / stress).
    P = np.array(
        [
            [0.97, 0.025, 0.005],
            [0.03, 0.94, 0.03],
            [0.01, 0.06, 0.93],
        ]
    )
    state = 1
    states = np.empty(t, dtype=np.int8)
    for i in range(t):
        states[i] = state
        state = int(g.choice(3, p=P[state]))

    # Daily log returns whose vol depends on regime.
    state_vol = np.array([0.008, 0.013, 0.028])
    daily_drift = -0.5 * state_vol[states] ** 2
    shocks = g.standard_normal(t) * state_vol[states] + daily_drift
    underlying = 100.0 * np.exp(np.cumsum(shocks))

    # Rolling 21d realized vol (annualized).
    rv = np.empty(t)
    win = 21
    for i in range(t):
        lo = max(0, i - win + 1)
        seg = shocks[lo : i + 1]
        rv[i] = float(np.std(seg, ddof=0) * np.sqrt(252)) if len(seg) > 1 else 0.15

    # Build SVI surfaces.
    k_grid = np.array(moneyness_grid, dtype=float)
    t_years = np.array(tenor_grid_days, dtype=float) / 365.0
    surfaces: list[np.ndarray] = []
    svi_params_per_day: list[dict[float, dict[str, float]]] = []

    for i in range(t):
        s = states[i]
        a = params.a0 + (params.stress_drift if s == 2 else 0.0) + 0.001 * g.standard_normal()
        b = params.b0 + 0.01 * g.standard_normal()
        rho = params.rho0 + (params.stress_skew if s == 2 else 0.0) + 0.02 * g.standard_normal()
        rho = float(np.clip(rho, -0.95, 0.95))
        m = params.m0 + 0.005 * g.standard_normal()
        sigma = max(0.05, params.sigma0 + 0.01 * g.standard_normal())

        # Term-structure: scale `a` linearly with sqrt(tenor).
        per_tenor: dict[float, dict[str, float]] = {}
        surf = np.empty((len(t_years), len(k_grid)))
        for j, ty in enumerate(t_years):
            a_j = a * (0.6 + 0.4 * np.sqrt(ty / max(t_years.max(), 1e-6)))
            sp = {"a": float(a_j), "b": float(b), "rho": float(rho), "m": float(m), "sigma": float(sigma)}
            per_tenor[float(ty)] = sp
            surf[j, :] = svi_iv(k_grid, ty, **sp)
        surfaces.append(surf)
        svi_params_per_day.append(per_tenor)

    return SyntheticPath(
        dates=dates,
        underlying=underlying,
        realized_vol_21d=rv,
        regime=states.astype(int),
        surfaces=surfaces,
        svi_params=svi_params_per_day,
        moneyness_grid=k_grid,
        tenor_grid_years=t_years,
    )
