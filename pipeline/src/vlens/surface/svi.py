"""Raw SVI fit + arbitrage checks.

Raw SVI total variance:
    w(k) = a + b * (rho * (k - m) + sqrt((k - m)^2 + sigma^2))

Bounds (necessary no-arb conditions enforced at fit time):
    b >= 0
    |rho| < 1
    sigma > 0
    a + b * sigma * sqrt(1 - rho^2) >= 0

Sufficient no-arb (butterfly + calendar) is checked **after** the fit and
recorded in ``SurfaceQuality`` rather than silently corrected.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize

from ..data.schemas import IVPoint, SVIParams


@dataclass(frozen=True)
class SVIFitResult:
    params: SVIParams
    rmse: float
    n_points: int


def _w(k: np.ndarray, a: float, b: float, rho: float, m: float, sigma: float) -> np.ndarray:
    return a + b * (rho * (k - m) + np.sqrt((k - m) ** 2 + sigma**2))


def _initial_guess(k: np.ndarray, w_obs: np.ndarray) -> np.ndarray:
    """ATM-anchored parabolic guess."""
    a0 = float(max(np.min(w_obs), 1e-4))
    b0 = float(max(0.05, (np.max(w_obs) - np.min(w_obs)) / max(1e-3, (np.max(k) - np.min(k)))))
    rho0 = -0.3
    m0 = float(k[np.argmin(w_obs)])
    sigma0 = 0.2
    return np.array([a0, b0, rho0, m0, sigma0], dtype=float)


def fit_svi_slice(
    points: list[IVPoint],
    *,
    b_min: float = 0.0,
    sigma_min: float = 1e-4,
    warm_start: SVIParams | None = None,
) -> SVIFitResult:
    """Fit SVI to a single tenor slice."""
    if len(points) < 5:
        raise ValueError("Need at least 5 IV points to fit SVI")

    tenor_years = points[0].tenor_years
    if any(abs(p.tenor_years - tenor_years) > 1e-9 for p in points):
        raise ValueError("All IVPoints in a slice must share the same tenor_years")

    k = np.array([p.log_moneyness for p in points], dtype=float)
    iv = np.array([p.iv for p in points], dtype=float)
    weights = np.array([max(p.weight, 1e-6) for p in points], dtype=float)
    w_obs = (iv**2) * tenor_years

    if warm_start is not None:
        x0 = np.array(
            [warm_start.a, warm_start.b, warm_start.rho, warm_start.m, warm_start.sigma],
            dtype=float,
        )
    else:
        x0 = _initial_guess(k, w_obs)

    bounds = [
        (-1.0, 5.0),               # a
        (b_min, 5.0),              # b
        (-0.999, 0.999),           # rho
        (float(k.min() - 1.0), float(k.max() + 1.0)),  # m
        (sigma_min, 5.0),          # sigma
    ]

    def loss(x: np.ndarray) -> float:
        a, b, rho, m, sigma = x
        # Soft penalty for the necessary no-arb condition
        # a + b*sigma*sqrt(1-rho^2) >= 0
        pen = max(0.0, -(a + b * sigma * float(np.sqrt(max(1.0 - rho**2, 0.0))))) * 100.0
        diff = _w(k, a, b, rho, m, sigma) - w_obs
        return float(np.sum(weights * diff**2)) + pen

    res = minimize(loss, x0=x0, method="L-BFGS-B", bounds=bounds)
    a, b, rho, m, sigma = (float(v) for v in res.x)
    fitted_w = _w(k, a, b, rho, m, sigma)
    fitted_iv = np.sqrt(np.clip(fitted_w / tenor_years, 1e-10, None))
    rmse = float(np.sqrt(np.mean((fitted_iv - iv) ** 2)))

    params = SVIParams(a=a, b=b, rho=rho, m=m, sigma=sigma)
    return SVIFitResult(params=params, rmse=rmse, n_points=len(points))


def svi_total_variance(k: np.ndarray, params: SVIParams) -> np.ndarray:
    return _w(k, params.a, params.b, params.rho, params.m, params.sigma)


def svi_iv_curve(k: np.ndarray, params: SVIParams, tenor_years: float) -> np.ndarray:
    w = svi_total_variance(k, params)
    return np.sqrt(np.clip(w / max(tenor_years, 1e-9), 1e-10, None))


def butterfly_violations(k: np.ndarray, params: SVIParams) -> int:
    """Count strict-convexity violations of total variance over `k`.

    Convex w(k) is a *necessary* condition for butterfly no-arb on a slice.
    """
    if len(k) < 3:
        return 0
    w = svi_total_variance(np.sort(k), params)
    # discrete second difference
    d2 = w[2:] - 2 * w[1:-1] + w[:-2]
    return int(np.sum(d2 < -1e-6))


def calendar_violations(
    params_by_tenor: dict[float, SVIParams],
    k_test: np.ndarray,
) -> int:
    """Count points where total variance is non-monotonic across tenors."""
    tenors = sorted(params_by_tenor.keys())
    if len(tenors) < 2:
        return 0
    matrix = np.stack([svi_total_variance(k_test, params_by_tenor[t]) for t in tenors], axis=0)
    violations = 0
    for i in range(1, len(tenors)):
        violations += int(np.sum(matrix[i] < matrix[i - 1] - 1e-6))
    return violations
