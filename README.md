# volatility-lens

A publicly hosted, interactive web product for **equity implied-volatility surfaces**, **skew/term-structure dynamics**, and **statistical market-regime classifications** — backed by a deterministic Python research pipeline that publishes versioned, signed JSON artifacts consumed by a Next.js front-end deployed to Vercel.

> Live URL: _to be set after first Vercel deploy_

This repo is a **two-stack monorepo**:

```
pipeline/   # Python 3.11 — research pipeline (SVI fit, HMM regime, signed artifacts)
web/        # Next.js 14 (App Router, TypeScript) — the public site
infra/      # GitHub Actions + Vercel config
docs/       # architecture, methodology, runbook, ADRs
```

## Quickstart

### Pipeline (Python)

```bash
cd pipeline
python -m pip install -e .[dev]
python -m vlens.cli publish --config configs/smoke.yaml --out artifacts/smoke
python -m vlens.cli verify  --bundle artifacts/smoke
python -m pytest -q
```

This produces a deterministic, signed artifact bundle under `pipeline/artifacts/smoke/` using a tiny synthetic SVI surface — **no API keys required**.

### Web (Next.js)

```bash
cd web
pnpm install
pnpm dev
```

The dev server reads the local smoke bundle from `pipeline/artifacts/smoke/` (see `web/lib/artifacts/client.ts`).

### One-shot smoke

```bash
make smoke      # build bundle + verify signature + JSON-schema-validate
make test       # pytest + vitest
```

## Architecture (one paragraph)

The Python pipeline ingests options data (synthetic by default; pluggable real-data adapters), fits a **raw SVI** parameterization per expiry slice (with explicit no-arbitrage checks), derives **skew/term-structure metrics** from the fitted surface (never raw quotes), runs a **Gaussian HMM** regime classifier with deterministic state labeling, and emits a **content-addressed, HMAC-signed JSON artifact bundle**. The Next.js web app statically renders pages against the latest bundle, with Edge routes serving artifact slices behind strong HTTP caching. The artifact bundle is the **only** contract between the two stacks; pydantic schemas in Python are exported to JSON Schema and code-generated into zod schemas in TypeScript so both sides validate the same shape.

See [`docs/architecture.md`](docs/architecture.md), [`docs/methodology.md`](docs/methodology.md), [`docs/deployment.md`](docs/deployment.md), and [`docs/decisions/`](docs/decisions/) for details.

## Status / phases

Implemented per [`MASTER_PROMPT.md`](MASTER_PROMPT.md) §11. Phase progress is tracked via ADRs and CI gates. The deterministic smoke path runs end-to-end in CI.

## License

MIT — see [`LICENSE`](LICENSE).
