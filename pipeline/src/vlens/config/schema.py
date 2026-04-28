"""Run-config schema (pydantic)."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class _Cfg(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UniverseCfg(_Cfg):
    tickers: list[str] = Field(min_length=1)


class DataCfg(_Cfg):
    source: Literal["synthetic", "yfinance", "csv"] = "synthetic"
    start: date
    end: date


class SVIBoundsCfg(_Cfg):
    b_min: float = 0.0
    sigma_min: float = 1.0e-4


class SVICfg(_Cfg):
    init: Literal["warm_start", "atm_parabolic"] = "warm_start"
    bounds: SVIBoundsCfg = SVIBoundsCfg()
    arb_check: Literal["strict", "warn"] = "warn"


class SurfaceCfg(_Cfg):
    moneyness_grid: list[float] = Field(min_length=2)
    tenor_grid_days: list[int] = Field(min_length=2)
    svi: SVICfg = SVICfg()


class RegimeCfg(_Cfg):
    model: Literal["hmm_gaussian_k2", "hmm_gaussian_k3", "changepoint_pelt"] = "hmm_gaussian_k3"
    features: list[str] = Field(min_length=1)
    refit_cadence: Literal["monthly", "quarterly", "yearly"] = "monthly"
    fit_window_years: int = 5


class SigningCfg(_Cfg):
    secret_env: str = "VLENS_PIPELINE_SECRET"


class UploadCfg(_Cfg):
    target: Literal["vercel_blob", "none"] = "none"


class PublishCfg(_Cfg):
    bundle_root: str = "pipeline/artifacts"
    signing: SigningCfg = SigningCfg()
    upload: UploadCfg = UploadCfg()


class RunConfig(_Cfg):
    seed: int = 42
    universe: UniverseCfg
    data: DataCfg
    surface: SurfaceCfg
    regime: RegimeCfg
    publish: PublishCfg = PublishCfg()
