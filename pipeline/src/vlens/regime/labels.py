"""Build the regime-feature matrix from a SkewMetric series + realized vol path.

Features (in fixed order, matching ``configs/*.yaml``):
    rv_21, iv_minus_rv, rr_25d, term_slope
"""

from __future__ import annotations

from datetime import date

import numpy as np

from ..data.schemas import SkewMetric


def build_features(
    skew: list[SkewMetric],
    realized_vol_21d: dict[date, float],
) -> tuple[list[date], np.ndarray]:
    skew_sorted = sorted(skew, key=lambda s: s.date)
    dates: list[date] = []
    rows: list[list[float]] = []
    for s in skew_sorted:
        rv = realized_vol_21d.get(s.date)
        if rv is None:
            continue
        rows.append(
            [
                float(rv),
                float(s.atm_iv_30d - rv),
                float(s.rr_25d),
                float(s.term_slope_30_90),
            ]
        )
        dates.append(s.date)
    return dates, np.array(rows, dtype=float)
