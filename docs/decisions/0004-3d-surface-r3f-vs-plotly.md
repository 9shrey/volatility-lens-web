# 0004 — 3D surface via react-three-fiber, not Plotly

**Status:** Accepted
**Date:** 2026-04

## Context
The IV surface is the headline visual. Two reasonable choices:
- **Plotly.js** (`Surface` trace) — out-of-the-box but ships ~2 MB even with the
  basic dist; mobile performance is poor.
- **react-three-fiber + drei** — declarative React over Three.js, code-splittable,
  GPU-accelerated, controllable bundle size (~150 KB gzipped for our usage).

## Decision
Use **react-three-fiber** for the 3D surface, dynamically imported and gated
behind a "Show 3D" toggle on small viewports. A 2D heatmap (no extra dep) is
the always-available SSR fallback.

## Consequences
- We own the camera/lighting code; in exchange we hit the §9.4 bundle budget.
- Accessibility: keyboard rotation, ARIA labels, and a `prefers-reduced-motion`
  fallback to the 2D heatmap are required, not optional.
