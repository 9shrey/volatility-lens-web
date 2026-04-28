"""SVI fit + arbitrage check basics."""

from __future__ import annotations

import numpy as np

from vlens.data.schemas import IVPoint, SVIParams
from vlens.surface.svi import (
    butterfly_violations,
    calendar_violations,
    fit_svi_slice,
    svi_iv_curve,
    svi_total_variance,
)


def _gen_slice(tenor: float = 0.25) -> list[IVPoint]:
    true = SVIParams(a=0.02, b=0.10, rho=-0.30, m=0.0, sigma=0.20)
    ks = np.linspace(-0.3, 0.3, 11)
    iv = svi_iv_curve(ks, true, tenor)
    return [
        IVPoint(log_moneyness=float(k), tenor_years=tenor, iv=float(v))
        for k, v in zip(ks, iv)
    ]


def test_fit_recovers_svi_to_low_rmse() -> None:
    pts = _gen_slice()
    res = fit_svi_slice(pts)
    assert res.rmse < 1e-3
    assert res.n_points == len(pts)


def test_butterfly_violations_zero_for_convex_slice() -> None:
    p = SVIParams(a=0.02, b=0.10, rho=-0.30, m=0.0, sigma=0.20)
    ks = np.linspace(-0.5, 0.5, 21)
    assert butterfly_violations(ks, p) == 0


def test_calendar_violations_detected_when_short_tenor_higher() -> None:
    short = SVIParams(a=0.40, b=0.10, rho=0.0, m=0.0, sigma=0.20)
    long = SVIParams(a=0.05, b=0.10, rho=0.0, m=0.0, sigma=0.20)
    ks = np.linspace(-0.1, 0.1, 5)
    # Total variance must be monotonic in tenor; here short>long deliberately.
    v = calendar_violations({0.25: short, 0.50: long}, ks)
    assert v > 0


def test_total_variance_matches_sqrt_iv_relation() -> None:
    p = SVIParams(a=0.02, b=0.10, rho=-0.30, m=0.0, sigma=0.20)
    k = np.array([0.0, 0.1])
    w = svi_total_variance(k, p)
    iv = svi_iv_curve(k, p, 0.25)
    np.testing.assert_allclose(iv, np.sqrt(w / 0.25), rtol=1e-9)
