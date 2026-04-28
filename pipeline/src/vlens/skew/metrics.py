"""Skew & term-structure metrics derived from a fitted SVI surface.

All metrics are *functions of the fitted SVI surface*, never raw quotes —
this is the no-arbitrage anchor.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm

from ..data.schemas import SVIParams
from ..surface.svi import svi_iv_curve


def bs_call_delta(k: float, sigma: float, t_years: float) -> float:
    """Black-Scholes call delta with r=0 in log-moneyness convention."""
    if sigma <= 0 or t_years <= 0:
        return 0.0
    sqrt_t = float(np.sqrt(t_years))
    d1 = (-k + 0.5 * sigma**2 * t_years) / (sigma * sqrt_t)
    return float(norm.cdf(d1))


def find_delta_strike(
    target_delta: float,
    *,
    is_call: bool,
    params: SVIParams,
    tenor_years: float,
    k_lo: float = -1.5,
    k_hi: float = 1.5,
) -> float:
    """Solve for log-moneyness whose BS delta hits ``target_delta``.

    Convention: ``target_delta`` is the absolute call delta; for puts we look
    for the strike where ``call_delta = 1 - target_delta`` (put delta = -target).
    """
    target = target_delta if is_call else (1.0 - target_delta)

    def f(k: float) -> float:
        sigma = float(svi_iv_curve(np.array([k]), params, tenor_years)[0])
        return bs_call_delta(k, sigma, tenor_years) - target

    f_lo, f_hi = f(k_lo), f(k_hi)
    if f_lo * f_hi > 0:
        # fall back to the closer endpoint
        return k_lo if abs(f_lo) < abs(f_hi) else k_hi
    return float(brentq(f, k_lo, k_hi, xtol=1e-6, maxiter=100))


def iv_at_delta(
    target_delta: float,
    *,
    is_call: bool,
    params: SVIParams,
    tenor_years: float,
) -> float:
    k = find_delta_strike(target_delta, is_call=is_call, params=params, tenor_years=tenor_years)
    return float(svi_iv_curve(np.array([k]), params, tenor_years)[0])


def atm_iv(params: SVIParams, tenor_years: float) -> float:
    return float(svi_iv_curve(np.array([0.0]), params, tenor_years)[0])


def risk_reversal_25d(params: SVIParams, tenor_years: float) -> float:
    iv_put = iv_at_delta(0.25, is_call=False, params=params, tenor_years=tenor_years)
    iv_call = iv_at_delta(0.25, is_call=True, params=params, tenor_years=tenor_years)
    return iv_put - iv_call


def butterfly_25d(params: SVIParams, tenor_years: float) -> float:
    iv_put = iv_at_delta(0.25, is_call=False, params=params, tenor_years=tenor_years)
    iv_call = iv_at_delta(0.25, is_call=True, params=params, tenor_years=tenor_years)
    return 0.5 * (iv_put + iv_call) - atm_iv(params, tenor_years)


def term_slope(params_30d: SVIParams, params_90d: SVIParams) -> float:
    return atm_iv(params_90d, 90 / 365.0) - atm_iv(params_30d, 30 / 365.0)
