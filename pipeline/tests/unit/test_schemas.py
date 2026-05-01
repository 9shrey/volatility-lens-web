"""Schema round-trip + boundary validation."""

from __future__ import annotations

from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError

from vlens.data.schemas import (
    GridSpec,
    IVPoint,
    OptionQuote,
    SurfaceQuality,
    SurfaceSnapshot,
    SVIParams,
)


def test_option_quote_ask_below_bid_rejected() -> None:
    with pytest.raises(ValidationError):
        OptionQuote(
            symbol="SPY",
            as_of=datetime(2024, 1, 2, tzinfo=UTC),
            expiry=date(2024, 6, 21),
            strike=400,
            option_type="C",
            bid=2.0,
            ask=1.0,
            underlying=410,
            rate=0.05,
        )


def test_svi_params_rho_bounds() -> None:
    with pytest.raises(ValidationError):
        SVIParams(a=0.0, b=0.1, rho=1.5, m=0.0, sigma=0.2)


def test_iv_point_positive_iv() -> None:
    with pytest.raises(ValidationError):
        IVPoint(log_moneyness=0.0, tenor_years=0.25, iv=-0.1)


def test_surface_snapshot_roundtrip() -> None:
    grid = GridSpec(log_moneyness=[-0.1, 0.0, 0.1], tenor_years=[0.25])
    snap = SurfaceSnapshot(
        symbol="SPY",
        as_of=date(2024, 1, 2),
        grid=grid,
        iv=[[0.2, 0.18, 0.21]],
        svi_params={"0.250000": SVIParams(a=0.02, b=0.1, rho=-0.3, m=0.0, sigma=0.2)},
        quality=SurfaceQuality(
            rmse_vs_market=0.001,
            n_quotes=3,
            interpolated_cells=0,
            butterfly_violations=0,
            calendar_violations=0,
        ),
    )
    dumped = snap.model_dump(mode="json")
    again = SurfaceSnapshot.model_validate(dumped)
    assert again == snap
