"""Build a SurfaceSnapshot for a single date from synthetic IV points.

Pipeline-facing entry: take per-tenor lists of ``IVPoint``, fit SVI on each
slice, sample onto canonical grid, count arb violations, return a
``SurfaceSnapshot``.
"""

from __future__ import annotations

from datetime import date

import numpy as np

from ..data.schemas import IVPoint, SurfaceQuality, SurfaceSnapshot, SVIParams
from .grid import make_grid
from .svi import (
    butterfly_violations,
    calendar_violations,
    fit_svi_slice,
    svi_iv_curve,
)


def build_surface(
    *,
    symbol: str,
    as_of: date,
    points_by_tenor: dict[float, list[IVPoint]],
    moneyness_grid: list[float],
    tenor_days: list[int],
    b_min: float = 0.0,
    sigma_min: float = 1e-4,
    warm_start: dict[float, SVIParams] | None = None,
) -> SurfaceSnapshot:
    grid = make_grid(moneyness_grid, tenor_days)
    k_arr = np.array(grid.log_moneyness, dtype=float)

    fit_results: dict[float, SVIParams] = {}
    rmses: list[float] = []
    n_quotes_total = 0
    bf_viol = 0

    for tenor_years in grid.tenor_years:
        # find matching points (closest tenor key)
        keys = list(points_by_tenor.keys())
        if not keys:
            raise ValueError("points_by_tenor is empty")
        nearest = min(keys, key=lambda k: abs(k - tenor_years))
        slice_pts = points_by_tenor[nearest]
        ws = warm_start.get(tenor_years) if warm_start else None
        res = fit_svi_slice(slice_pts, b_min=b_min, sigma_min=sigma_min, warm_start=ws)
        fit_results[tenor_years] = res.params
        rmses.append(res.rmse)
        n_quotes_total += res.n_points
        bf_viol += butterfly_violations(k_arr, res.params)

    iv_grid: list[list[float]] = []
    for tenor_years in grid.tenor_years:
        curve = svi_iv_curve(k_arr, fit_results[tenor_years], tenor_years)
        iv_grid.append([float(x) for x in curve])

    cal_viol = calendar_violations(fit_results, k_arr)

    quality = SurfaceQuality(
        rmse_vs_market=float(np.mean(rmses)),
        n_quotes=n_quotes_total,
        interpolated_cells=0,
        butterfly_violations=bf_viol,
        calendar_violations=cal_viol,
    )

    # Convert tenor-year keys to canonical strings for JSON.
    svi_str = {f"{t:.6f}": p for t, p in fit_results.items()}

    return SurfaceSnapshot(
        symbol=symbol,
        as_of=as_of,
        grid=grid,
        iv=iv_grid,
        svi_params=svi_str,
        quality=quality,
    )
