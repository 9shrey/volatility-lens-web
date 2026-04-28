"""Skew metric sanity tests."""

from __future__ import annotations

from vlens.data.schemas import SVIParams
from vlens.skew.metrics import atm_iv, butterfly_25d, risk_reversal_25d, term_slope


def test_atm_iv_positive() -> None:
    p = SVIParams(a=0.02, b=0.10, rho=-0.30, m=0.0, sigma=0.20)
    assert atm_iv(p, 30 / 365.0) > 0


def test_negative_rho_yields_positive_risk_reversal() -> None:
    """A standard equity skew (rho<0) should give IV(put) > IV(call)."""
    p = SVIParams(a=0.02, b=0.20, rho=-0.6, m=0.0, sigma=0.20)
    assert risk_reversal_25d(p, 30 / 365.0) > 0


def test_symmetric_smile_has_smaller_rr_than_skewed() -> None:
    """With rho=0 the smile is centered; a negative-rho smile must give larger |RR|."""
    sym = SVIParams(a=0.04, b=0.10, rho=0.0, m=0.0, sigma=0.30)
    skewed = SVIParams(a=0.04, b=0.10, rho=-0.6, m=0.0, sigma=0.30)
    assert abs(risk_reversal_25d(sym, 30 / 365.0)) < abs(
        risk_reversal_25d(skewed, 30 / 365.0)
    )


def test_butterfly_positive_for_smile() -> None:
    p = SVIParams(a=0.02, b=0.20, rho=0.0, m=0.0, sigma=0.10)
    assert butterfly_25d(p, 30 / 365.0) > 0


def test_term_slope_positive_when_long_total_variance_higher() -> None:
    """Term slope is in *vol* space; long-end ATM total variance must beat the
    short-end after dividing by tenor."""
    short = SVIParams(a=0.02, b=0.1, rho=0.0, m=0.0, sigma=0.2)
    long = SVIParams(a=0.20, b=0.1, rho=0.0, m=0.0, sigma=0.2)
    assert term_slope(short, long) > 0
