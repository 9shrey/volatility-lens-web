# Bias / Honesty Checklist

This document encodes the bias and integrity rules that the pipeline and website must obey. Each item is paired with the place where it is enforced (test, gate, or design decision).

## No look-ahead

- Regime fit on day `t` uses **only** observations with `as_of <= t - 1 business day`.
  - Enforced in `pipeline/src/vlens/regime/hmm.py` via a `cutoff: date` argument; using any data with `as_of > cutoff` raises `LookaheadError`.
  - Property test: `pipeline/tests/property/test_no_lookahead.py` shifts input series by `k` bars and asserts every derived series shifts by exactly `k` bars.
- SVI surface fit on day `t` uses **only** option quotes with `as_of <= t`.

## No survivorship bias

- Ticker universe is **point-in-time**. If a ticker delists, the site shows it as `discontinued` rather than silently dropping it from the universe.
- Universe membership is recorded with `from_date` / `to_date` in `pipeline/configs/*.yaml`.

## No paid-data leakage in CI

- The default and smoke configs use the **synthetic SVI generator** (`pipeline/src/vlens/data/synthetic.py`).
- Real-data adapters (yfinance, csv) are gated behind `data.source` and clearly labeled in the UI as `Source: <adapter>`. CI runs the synthetic path only.

## No silent imputation

- Every interpolated cell is flagged in `SurfaceQuality.interpolated_cells` and rendered in the UI with a distinct hatched pattern.
- Surfaces with arbitrage violations (butterfly / calendar) carry counts in `SurfaceQuality.butterfly_violations` / `calendar_violations` and the UI surfaces a warning badge — they are **not** silently corrected.

## No misleading visuals

- Dual-axis charts are forbidden (lint rule documented in `docs/visual-design.md`).
- Truncated y-axes are always annotated with a "axis truncated" badge.
- Regime states are encoded with **shape + label + color**, never color alone (color-blind safe Okabe-Ito palette + hatched ribbon segments + ARIA labels).

## Provenance on every datum

- Every chart hover surfaces `as_of`, `source`, `pipeline_run_id`, and the bundle SHA.
- A visible "Get data" button lets the user download the underlying JSON for the current view.

## Determinism

- Same seed + same inputs ⇒ bit-identical artifact bundle (verified by SHA-256 in CI).
- Floats are serialized with fixed 8-decimal precision; JSON keys sorted; LF line endings.

## Signed artifacts

- Every bundle's `manifest.json` carries an HMAC-SHA256 signature over the canonical manifest.
- The web edge route refuses unsigned/tampered bundles with `502`.
