"""Build daily skew & term-structure time series from a list of SurfaceSnapshots."""

from __future__ import annotations

from datetime import date

from ..data.schemas import SkewMetric, SurfaceSnapshot, SVIParams, TermPoint
from .metrics import atm_iv, butterfly_25d, risk_reversal_25d, term_slope


def _params_for_tenor_years(snap: SurfaceSnapshot, target_years: float) -> tuple[float, SVIParams]:
    keys = list(snap.svi_params.keys())
    nearest = min(keys, key=lambda k: abs(float(k) - target_years))
    return float(nearest), snap.svi_params[nearest]


def daily_skew_series(snapshots: list[SurfaceSnapshot]) -> list[SkewMetric]:
    """Compute one row per snapshot, ordered by date."""
    out: list[SkewMetric] = []
    for snap in sorted(snapshots, key=lambda s: s.as_of):
        t30, p30 = _params_for_tenor_years(snap, 30 / 365.0)
        t90, p90 = _params_for_tenor_years(snap, 90 / 365.0)
        rr = risk_reversal_25d(p30, t30)
        bf = butterfly_25d(p30, t30)
        atm = atm_iv(p30, t30)
        slope = term_slope(p30, p90) if t90 != t30 else 0.0
        out.append(
            SkewMetric(
                date=snap.as_of,
                rr_25d=float(rr),
                bf_25d=float(bf),
                atm_iv_30d=float(atm),
                term_slope_30_90=float(slope),
            )
        )
    return out


def daily_term_structure(
    snapshots: list[SurfaceSnapshot],
    tenor_days: list[int],
) -> list[TermPoint]:
    """Emit one row per (date, tenor) of ATM IV."""
    out: list[TermPoint] = []
    for snap in sorted(snapshots, key=lambda s: s.as_of):
        for d in tenor_days:
            ty = d / 365.0
            t_actual, p = _params_for_tenor_years(snap, ty)
            iv = atm_iv(p, t_actual)
            out.append(TermPoint(date=snap.as_of, tenor_days=d, atm_iv=float(iv)))
    return out


__all__ = ["daily_skew_series", "daily_term_structure"]


# Re-export helper for tests/CLI
def coerce_date(d: date) -> date:  # pragma: no cover - trivial
    return d
