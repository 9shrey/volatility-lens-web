# 0003 — Artifact-driven website (no live API at request time)

**Status:** Accepted
**Date:** 2026-04

## Context
We could call data APIs (yfinance, Polygon, OptionMetrics) at request time, but
that introduces latency, paid-API spend, request-time secrets, and per-page-view
non-determinism — all of which conflict with the public-website use case.

## Decision
The web app **never** calls a paid data API at runtime. The single contract
between Python and TypeScript is the **immutable, signed artifact bundle**
defined in `MASTER_PROMPT.md` §7. Edge routes only read from this bundle.

## Consequences
- The website is fast, cacheable, and survives upstream provider outages.
- A fresh dataset requires a pipeline run + bundle promotion, not a deploy.
- Every datum carries provenance (`pipeline_git_sha`, `inputs_hash`,
  `produced_at`) and the bundle is HMAC-signed so the edge can refuse tampered
  inputs.
