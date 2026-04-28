# 0007 — Schema codegen: pydantic → JSON Schema → zod

**Status:** Accepted
**Date:** 2026-04

## Context
The artifact bundle is the single contract between Python and TypeScript. We
must keep the two stacks' type definitions in lockstep without a hand-edit
ritual that drifts.

## Decision
- **pydantic** is the source of truth (`pipeline/src/vlens/data/schemas.py`).
- `vlens schema export` writes a JSON Schema bundle to `web/lib/artifacts/`.
- `pnpm gen:schemas` converts the JSON Schema to a `schemas.generated.ts` zod file.
- A hand-written `schemas.ts` pins the public types we actually consume; CI fails
  if `schemas.generated.ts` drifts from the exported JSON Schema.

## Consequences
- We never edit `schemas.generated.ts` by hand.
- Breaking schema changes require an ADR and a `schema_version` bump in `manifest.json`.
- The runtime pays a tiny zod-validation cost in exchange for honest validation
  errors at the edge instead of silent UI breakage.
