# Deployment

## One-time Vercel setup

1. Create a new Vercel project pointed at this repo.
2. **Root Directory** = `15-volatility-lens-web/web`.
3. Framework Preset = Next.js, Node = 20.x.
4. Set the environment variables documented in `infra/vercel/env.example.md`.
5. Connect the GitHub Action `pipeline.yml` to the project's Blob store
   (`VLENS_BLOB_RW_TOKEN`) and surface `VLENS_BLOB_BASE_URL` as a project var.

## What CI does on every PR

- `ci.yml` runs lint, typecheck, unit tests for both stacks; asserts the smoke
  bundle is bit-identical across two runs.
- `e2e.yml` builds a fresh smoke bundle into `web/public/_smoke_bundle/` and
  runs the Playwright suite against it.

## What the nightly does

- `pipeline.yml` runs `vlens publish --config configs/full.yaml`, signs the
  bundle, uploads to Vercel Blob, and updates `VLENS_BUNDLE_VERSION` on the
  Vercel project to trigger a redeploy.
