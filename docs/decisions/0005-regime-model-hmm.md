# 0005 — Regime model: Gaussian HMM (k = 2, 3) baseline

**Status:** Accepted
**Date:** 2026-04

## Context
We want a regime classifier that is (a) interpretable, (b) deterministic given
a seed, (c) cheap to retrain monthly on commodity hardware, and (d) honest about
its causal structure (no look-ahead).

## Decision
Use a **Gaussian HMM** from `hmmlearn` with K ∈ {2, 3}. Provide a
**change-point baseline** (`ruptures` PELT) for visual comparison only.

## Consequences
- Forecasting is explicitly out of scope (Project 14 owns DL forecasting).
- States are labeled deterministically by ranking on unconditional mean realized
  vol so the UI legend is stable across re-fits.
- Refit is monthly on a strictly past window; predictions on test days use a
  causal forward filter only.
