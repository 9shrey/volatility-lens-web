"""pydantic schemas for raw and derived data structures.

These are the **wire types** that round-trip through canonical JSON. Every
field that ends up in a published artifact must be representable as JSON.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class OptionQuote(_Frozen):
    """A single option quote at a point in time."""

    symbol: str
    as_of: datetime
    expiry: date
    strike: float = Field(gt=0)
    option_type: Literal["C", "P"]
    bid: float = Field(ge=0)
    ask: float = Field(ge=0)
    underlying: float = Field(gt=0)
    rate: float
    iv: float | None = None

    @field_validator("ask")
    @classmethod
    def _ask_ge_bid(cls, v: float, info) -> float:  # type: ignore[no-untyped-def]
        bid = info.data.get("bid")
        if bid is not None and v < bid:
            raise ValueError("ask must be >= bid")
        return v


class IVPoint(_Frozen):
    log_moneyness: float
    tenor_years: float = Field(gt=0)
    iv: float = Field(gt=0)
    weight: float = Field(ge=0, default=1.0)


class GridSpec(_Frozen):
    log_moneyness: list[float]
    tenor_years: list[float]


class SVIParams(_Frozen):
    """Raw SVI: w(k) = a + b*(rho*(k-m) + sqrt((k-m)^2 + sigma^2))."""

    a: float
    b: float = Field(ge=0)
    rho: float = Field(ge=-0.999, le=0.999)
    m: float
    sigma: float = Field(gt=0)


class SurfaceQuality(_Frozen):
    rmse_vs_market: float = Field(ge=0)
    n_quotes: int = Field(ge=0)
    interpolated_cells: int = Field(ge=0)
    butterfly_violations: int = Field(ge=0)
    calendar_violations: int = Field(ge=0)


class SurfaceSnapshot(_Frozen):
    symbol: str
    as_of: date
    grid: GridSpec
    iv: list[list[float]]                # shape: [n_tenor][n_moneyness]
    svi_params: dict[str, SVIParams]     # tenor (string-keyed for JSON) -> SVIParams
    quality: SurfaceQuality


class SkewMetric(_Frozen):
    date: date
    rr_25d: float
    bf_25d: float
    atm_iv_30d: float
    term_slope_30_90: float


class TermPoint(_Frozen):
    date: date
    tenor_days: int
    atm_iv: float


class RegimeStateRow(_Frozen):
    date: date
    state: int = Field(ge=0)
    posterior: list[float]


class RegimeSnapshot(_Frozen):
    symbol: str
    model: Literal["hmm_gaussian_k2", "hmm_gaussian_k3", "changepoint_pelt"]
    fit_window: tuple[date, date]
    states: list[RegimeStateRow]
    state_labels: dict[str, str]         # str-int -> label
    seed: int


class TickerIndexEntry(_Frozen):
    symbol: str
    latest_date: date
    n_dates: int


class TickerIndex(_Frozen):
    tickers: list[TickerIndexEntry]
    as_of: date
    manifest_version: str


class Manifest(_Frozen):
    schema_version: str
    pipeline_git_sha: str
    produced_at: datetime
    inputs_hash: str
    bundle_id: str
    signature: str = ""                  # filled at sign time


__all__ = [
    "OptionQuote",
    "IVPoint",
    "GridSpec",
    "SVIParams",
    "SurfaceQuality",
    "SurfaceSnapshot",
    "SkewMetric",
    "TermPoint",
    "RegimeStateRow",
    "RegimeSnapshot",
    "TickerIndexEntry",
    "TickerIndex",
    "Manifest",
]
