# 0006 — Raw SVI parameterization for surface fits

**Status:** Accepted
**Date:** 2026-04

## Context
Candidate parameterizations: SSVI, raw SVI, natural SVI, polynomial fits.
We need: per-slice fits, easy enforcement of necessary no-arbitrage bounds,
warm-starts across days, and code that an interviewer can read in a sitting.

## Decision
Use **raw SVI** per tenor slice:
`w(k) = a + b·(ρ·(k − m) + √((k − m)² + σ²))`, fit by L-BFGS-B with the
necessary no-arb bound enforced as a soft penalty. Sufficient no-arb
(butterfly + calendar) is **checked, not enforced** — violations are recorded
in `SurfaceQuality`.

## Consequences
- Per-slice fits are fast and warm-startable from the previous trading day.
- We do not silently correct arb violations; the UI surfaces them as a quality flag.
- Calendar arbitrage across slices is a separate test, not a constrained joint fit.
