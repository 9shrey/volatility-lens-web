"""Canonical (log-moneyness x tenor) grid construction."""

from __future__ import annotations

from ..data.schemas import GridSpec


def make_grid(moneyness: list[float], tenor_days: list[int]) -> GridSpec:
    if sorted(moneyness) != list(moneyness):
        raise ValueError("moneyness grid must be strictly increasing")
    if sorted(tenor_days) != list(tenor_days):
        raise ValueError("tenor_days grid must be strictly increasing")
    return GridSpec(
        log_moneyness=list(moneyness),
        tenor_years=[d / 365.0 for d in tenor_days],
    )
