"""SVI invariants on synthetic surfaces."""

from __future__ import annotations

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from vlens.data.schemas import IVPoint, SVIParams
from vlens.surface.svi import fit_svi_slice, svi_iv_curve


@given(
    a=st.floats(min_value=0.005, max_value=0.05),
    b=st.floats(min_value=0.05, max_value=0.30),
    rho=st.floats(min_value=-0.6, max_value=0.6),
    sigma=st.floats(min_value=0.1, max_value=0.4),
)
@settings(max_examples=15, deadline=None)
def test_svi_fit_recovers_synthetic_iv_within_tolerance(
    a: float, b: float, rho: float, sigma: float
) -> None:
    p = SVIParams(a=a, b=b, rho=rho, m=0.0, sigma=sigma)
    tenor = 0.25
    ks = np.linspace(-0.3, 0.3, 11)
    iv = svi_iv_curve(ks, p, tenor)
    pts = [
        IVPoint(log_moneyness=float(k), tenor_years=tenor, iv=float(v))
        for k, v in zip(ks, iv, strict=True)
    ]
    res = fit_svi_slice(pts)
    fitted = svi_iv_curve(ks, res.params, tenor)
    np.testing.assert_allclose(fitted, iv, atol=2e-2)
