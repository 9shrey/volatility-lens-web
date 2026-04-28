# 0002 — Vercel as the deployment target

**Status:** Accepted
**Date:** 2026-04

## Context
We need: zero-ops global CDN, preview deploys per PR, free TLS, edge runtime,
analytics that respect privacy, and a public URL a recruiter can open on a phone.

## Decision
Deploy the `web/` package to **Vercel**. The Python pipeline publishes
artifacts to **Vercel Blob**, content-addressed, behind the same edge.

## Consequences
- Vendor lock-in for hosting; mitigated by keeping the artifact bundle a plain
  set of JSON files reachable over HTTP — any CDN can serve them.
- Promotion + rollback both reduce to setting `VLENS_BUNDLE_VERSION` and
  redeploying. Documented in `docs/runbook.md`.
