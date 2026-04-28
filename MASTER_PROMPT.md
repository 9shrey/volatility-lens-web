# MASTER PROMPT — Volatility & Regime Lens (Project 15)

> Single source of truth for an autonomous coding agent (or human contributor) building this project end-to-end. It encodes scope, architecture, interfaces, acceptance criteria, the Vercel deployment contract, and a phased execution plan. Do not deviate from the contracts in §6 or the artifact schema in §7 without an ADR.

---

## 1. Project Identity

- **Name:** `volatility-lens`
- **One-liner:** A publicly hosted, interactive web product that visualizes equity implied-volatility surfaces, skew/term-structure dynamics, and statistical market-regime classifications — backed by a deterministic Python research pipeline that nightly publishes versioned, signed JSON artifacts consumed by a Next.js front-end deployed to Vercel.
- **Domain:** Quantitative Finance · Time-Series ML · Data Visualization · Web Engineering
- **Primary persona:** Quant researcher / ML engineer interviewing for HF, prop, options-desk, fintech, or DS-platform roles where the ability to *ship visible, defensible analytics to a public audience* is a differentiator.
- **Why it exists:** Most ML/quant repos live as CLIs and notebooks. This project demonstrates the full last mile: a reproducible research pipeline whose output is a fast, accessible, citable **website** that a recruiter, trader, or PM can open on a phone and trust.
- **Distinguishing feature vs the rest of the track:** the *deliverable is a deployed URL*, not a CLI. The Python pipeline exists to feed the website; the website is the artifact.

---

## 2. Outcomes & Success Criteria

A reviewer must be able to:

1. Open the deployed URL and, in < 3 seconds on a cold load over 4G, see:
   - A 3D implied-volatility surface for a default ticker (e.g. `SPY`) for the latest available date.
   - A skew-vs-moneyness chart for the front three expiries.
   - A term-structure (ATM IV vs days-to-expiry) chart.
   - A regime ribbon (HMM state probabilities over the last 5 years) under the price chart.
2. Switch ticker, date, and regime model from the URL bar (deep-linkable state).
3. Hover any chart point and see precise values + provenance (`as_of`, `source`, `pipeline_run_id`).
4. Download the underlying JSON artifact for the currently displayed view via a visible "Get data" button.
5. Run `make dev` locally and reproduce the same site against a tiny synthetic fixture, with no API keys required.
6. Run `make publish` and produce a fresh artifact bundle that the Next.js app loads identically in `next dev` and in a Vercel preview deployment.

**Definition of Done (hard gates):**
- ≥ 90 % unit-test coverage on `pipeline/` (Python) and ≥ 80 % on `web/lib/` (TypeScript).
- Property tests in Python: no look-ahead in regime/skew features, monotonic time index, deterministic outputs given seed.
- E2E tests with Playwright: home page renders, ticker switch updates surface, deep link restores state, "Get data" downloads valid JSON matching the schema in §7.
- **Lighthouse** scores on production build: Performance ≥ 90, Accessibility ≥ 95, Best Practices ≥ 95, SEO ≥ 95 (mobile profile).
- **Bundle budget**: initial route JS ≤ 180 KB gzip; 3D surface chunk lazy-loaded only on the surface tab.
- Deterministic pipeline: same seed + same fixture → bit-identical artifact JSON (verified by SHA-256 in CI).
- Every artifact carries a manifest with `schema_version`, `pipeline_git_sha`, `produced_at`, `inputs_hash`, `signature` (HMAC over content using a repo-stored public-verifiable key — see §7.4).
- ADRs filed for every irreversible choice (see §11).
- A live, public Vercel URL is documented in the README; preview URLs auto-post on PRs.

---

## 3. Non-Goals

- **No live trading, brokerage integration, or order routing.**
- **No paid data dependency in the default path.** The repo must run end-to-end on a synthetic SVI-based generator. Real-data adapters (yfinance, Polygon, CBOE, OptionMetrics) are pluggable and disabled in CI.
- **No user accounts, no PII, no server-side persistence of visitor data.** The site is a read-only data product.
- **No custom DL research.** Regime model is a Gaussian HMM (and a change-point baseline). Forecasting is *not* the focus — this is a *visualization & explanatory analytics* product. Heavy DL forecasting belongs in Project 14.
- **No SSR with per-request DB hits.** Pages are statically generated against pre-built artifacts; only a small set of edge functions exist for on-demand queries (§5.4).
- **No multi-tenant features.** Single curated universe of \~25 tickers, configurable.

---

## 4. Tech Stack (locked)

### 4.1 Python pipeline (`pipeline/`)

| Layer | Choice | Rationale |
|---|---|---|
| Language | Python 3.11 | Same as rest of track |
| Package manager | `uv` | Fast, reproducible, lockfile-first |
| Data | `polars` (primary), `pandas` (interop) | Speed + correctness on bar/option data |
| Numerics | `numpy`, `scipy` | — |
| Options math | Custom Black-Scholes + SVI fitter (`scipy.optimize`) | Auditable, no heavy options-pricing dep |
| Regime model | `hmmlearn` (Gaussian HMM) + `ruptures` (change-point baseline) | Standard, interpretable |
| Validation | `pydantic v2` | Typed boundaries, JSON-schema export |
| Config | YAML + pydantic | Diffable, typed |
| CLI | `typer` | Auto-help, ergonomic |
| Tests | `pytest`, `hypothesis`, `pytest-cov` | Unit + property + coverage |
| Lint/format | `ruff`, `black`, `mypy --strict` on `pipeline/src/` | — |
| Artifact storage (prod) | Vercel Blob (primary), GitHub Releases (mirror) | Versioned, public, CDN-fronted |
| Artifact storage (local) | `pipeline/artifacts/` (gitignored) | — |

**Forbidden in pipeline:** TensorFlow, PyTorch, network calls during tests, hardcoded secrets, hardcoded paths, paid-data dependencies in default config.

### 4.2 Web front-end (`web/`)

| Layer | Choice | Rationale |
|---|---|---|
| Framework | **Next.js 14 (App Router)**, TypeScript strict | First-class on Vercel, RSC + edge support, mature |
| Runtime targets | Node 20 (build), Edge Runtime (selected routes) | Match Vercel offering |
| UI | React 18, Tailwind CSS, shadcn/ui (Radix primitives) | Accessible, themeable, low-bundle |
| 2D charts | **Plotly.js (basic dist) lazy-loaded** OR **Recharts** for low-bundle paths | Plotly for surface/heatmaps, Recharts for ribbons & lines |
| 3D surface | **react-three-fiber + drei** | Mature, declarative, GPU-accelerated, works on mobile |
| State | URL-as-state via `nuqs`, plus `zustand` for ephemeral UI | Deep-linkable, no Redux ceremony |
| Data fetching | Native `fetch` with Next.js cache + ISR for artifact JSON | CDN-friendly |
| Validation (TS) | `zod` mirrors of pydantic schemas | One source of truth via codegen (§7.5) |
| Testing | `vitest` (unit), `@testing-library/react`, `playwright` (e2e) | Standard |
| Lint/format | `eslint` (next config), `prettier`, `tsc --noEmit` strict | — |
| Analytics | Vercel Analytics (privacy-friendly) + `@vercel/speed-insights` | Zero-config, cookieless |
| Deployment | **Vercel** (production + preview-per-PR) | Locked target |

**Forbidden in web:** client-side secrets, runtime calls to paid APIs, importing the entire Plotly bundle on the home route, blocking JS in `<head>`, any `dangerouslySetInnerHTML` of pipeline output without zod validation.

### 4.3 Glue

| Concern | Choice |
|---|---|
| Monorepo | pnpm workspaces (web) + uv project (pipeline), coordinated by root `Makefile` |
| CI | GitHub Actions: lint + type + test (both stacks) + pipeline smoke + e2e on a Vercel preview |
| Releases | Conventional commits + `release-please`; pipeline artifact versioning is independent (§7) |
| Pre-commit | `ruff`, `prettier`, `eslint --fix`, `mypy`, `tsc` |

---

## 5. Repository Layout

```
15-volatility-lens-web/
├── README.md                       # quickstart + live URL + screenshots
├── MASTER_PROMPT.md                # this file
├── LICENSE                         # MIT
├── Makefile                        # one-liners that span both stacks
├── .gitignore
├── .editorconfig
├── .nvmrc                          # 20.x
├── .python-version                 # 3.11
├── vercel.json                     # build, routes, headers, edge config
├── pnpm-workspace.yaml
│
├── pipeline/                       # Python research pipeline
│   ├── pyproject.toml              # uv-managed, pinned
│   ├── uv.lock
│   ├── src/vlens/
│   │   ├── __init__.py
│   │   ├── cli.py                  # typer entrypoint: `vlens ...`
│   │   ├── config/
│   │   │   ├── schema.py           # pydantic models for run config
│   │   │   └── loader.py
│   │   ├── data/
│   │   │   ├── synthetic.py        # SVI-based surface generator (CI-default)
│   │   │   ├── adapters/
│   │   │   │   ├── yfinance.py     # optional, behind feature flag
│   │   │   │   └── csv.py
│   │   │   └── schemas.py          # OptionQuote, IVPoint, Bar
│   │   ├── surface/
│   │   │   ├── svi.py              # raw SVI parameterization + fit
│   │   │   ├── grid.py             # canonical (log-moneyness × tenor) grid
│   │   │   └── interpolate.py      # constrained interpolation, NaN policy
│   │   ├── skew/
│   │   │   ├── metrics.py          # 25Δ risk-reversal, butterfly, ATM, term slope
│   │   │   └── series.py           # build daily metric time series
│   │   ├── regime/
│   │   │   ├── hmm.py              # Gaussian HMM fit + forward-filter predict
│   │   │   ├── changepoint.py      # ruptures-based baseline
│   │   │   └── labels.py           # state → human-readable label mapping
│   │   ├── publish/
│   │   │   ├── artifacts.py        # builds the JSON artifact bundle (§7)
│   │   │   ├── manifest.py         # produces signed manifest.json
│   │   │   ├── upload_vercel.py    # uploads to Vercel Blob (skipped locally)
│   │   │   └── jsonschema_export.py # exports zod-compatible JSON schema
│   │   └── utils/
│   │       ├── seeding.py
│   │       ├── logging.py          # structlog
│   │       ├── hashing.py          # canonical JSON hash + HMAC sign/verify
│   │       └── io.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── property/               # hypothesis: monotonic time, no look-ahead
│   │   ├── integration/            # full pipeline → artifact → schema validates
│   │   └── fixtures/               # tiny deterministic synthetic data
│   ├── configs/
│   │   ├── default.yaml
│   │   ├── smoke.yaml              # 1 ticker, 90 days, deterministic
│   │   └── full.yaml
│   ├── artifacts/                  # gitignored output of `vlens publish`
│   └── README.md
│
├── web/                            # Next.js 14 app
│   ├── package.json
│   ├── next.config.mjs
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── postcss.config.mjs
│   ├── playwright.config.ts
│   ├── vitest.config.ts
│   ├── public/
│   │   ├── favicon.ico
│   │   └── og.png                  # social card
│   ├── app/                        # App Router
│   │   ├── layout.tsx              # global shell, theme, fonts
│   │   ├── page.tsx                # landing: latest snapshot of default ticker
│   │   ├── (lens)/
│   │   │   ├── ticker/[symbol]/page.tsx        # main lens view
│   │   │   └── ticker/[symbol]/[date]/page.tsx # historical snapshot
│   │   ├── about/page.tsx          # methodology, citations
│   │   ├── methodology/page.tsx    # rendered MDX from docs/
│   │   ├── api/
│   │   │   ├── snapshot/route.ts   # edge: returns artifact slice (cached)
│   │   │   ├── tickers/route.ts    # edge: enumerates universe
│   │   │   └── healthz/route.ts    # node: health
│   │   ├── opengraph-image.tsx     # dynamic OG image per ticker
│   │   ├── robots.ts
│   │   └── sitemap.ts
│   ├── components/
│   │   ├── charts/
│   │   │   ├── Surface3D.tsx       # react-three-fiber, lazy-loaded
│   │   │   ├── SkewChart.tsx       # Recharts
│   │   │   ├── TermStructure.tsx   # Recharts
│   │   │   ├── RegimeRibbon.tsx    # Recharts + custom legend
│   │   │   └── PriceWithRegime.tsx
│   │   ├── controls/
│   │   │   ├── TickerPicker.tsx
│   │   │   ├── DateScrubber.tsx
│   │   │   └── ModelToggle.tsx
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── ProvenanceBadge.tsx
│   │   └── ui/                     # shadcn primitives (button, dialog, etc.)
│   ├── lib/
│   │   ├── artifacts/
│   │   │   ├── client.ts           # fetch + zod-validate artifacts
│   │   │   ├── schemas.ts          # zod mirrors of pydantic (codegen target)
│   │   │   └── cache.ts
│   │   ├── url-state.ts            # nuqs-based state parsers
│   │   ├── analytics.ts
│   │   └── env.ts                  # zod-validated runtime env
│   ├── content/
│   │   └── methodology.mdx         # rendered into /methodology
│   ├── tests/
│   │   ├── unit/
│   │   └── e2e/                    # playwright specs
│   └── README.md
│
├── infra/
│   ├── github/
│   │   └── workflows/
│   │       ├── ci.yml              # lint + type + unit (both stacks)
│   │       ├── pipeline.yml        # nightly: build artifact, sign, upload to Blob
│   │       ├── e2e.yml             # on PR: spin Vercel preview, run Playwright
│   │       └── release.yml         # release-please
│   └── vercel/
│       ├── env.example.md          # documents required Vercel envs
│       └── README.md
│
└── docs/
    ├── architecture.md
    ├── methodology.md              # SVI fit, regime model, no-lookahead contract
    ├── runbook.md                  # how to publish, rollback, debug a bad artifact
    ├── deployment.md               # Vercel project setup, custom domain, envs
    ├── visual-design.md            # color tokens, chart conventions, a11y notes
    └── decisions/                  # ADRs
        ├── 0001-nextjs-app-router.md
        ├── 0002-vercel-as-target.md
        ├── 0003-artifact-driven-vs-live-api.md
        ├── 0004-3d-surface-r3f-vs-plotly.md
        ├── 0005-regime-model-hmm.md
        ├── 0006-svi-parameterization.md
        ├── 0007-schema-codegen-pydantic-to-zod.md
        └── README.md
```

---

## 6. Public Interfaces (contracts)

These signatures are **stable**. Implementations may evolve; signatures may not without an ADR.

### 6.1 Pipeline data schemas (pydantic)

```python
class OptionQuote(BaseModel):
    symbol: str
    as_of: datetime          # tz-aware UTC, end-of-day
    expiry: date
    strike: float
    option_type: Literal["C", "P"]
    bid: float
    ask: float
    underlying: float
    rate: float              # risk-free
    iv: float | None         # if vendor-provided; else computed

class IVPoint(BaseModel):
    log_moneyness: float
    tenor_years: float
    iv: float
    weight: float            # used in SVI fit

class SurfaceSnapshot(BaseModel):
    symbol: str
    as_of: date
    grid: GridSpec           # canonical axes
    iv: list[list[float]]    # shape: [n_tenor][n_moneyness]
    svi_params: dict[float, SVIParams]   # tenor → SVI params
    quality: SurfaceQuality  # rmse vs market, % cells interpolated, arb-violations
```

### 6.2 Regime contract

```python
class RegimeSnapshot(BaseModel):
    symbol: str
    model: Literal["hmm_gaussian_k2", "hmm_gaussian_k3", "changepoint_pelt"]
    fit_window: tuple[date, date]      # train-only window
    states: list[RegimeStateRow]       # one row per business day
    state_labels: dict[int, str]       # 0 -> "low_vol", 1 -> "stress", ...
    seed: int

class RegimeStateRow(BaseModel):
    date: date
    state: int
    posterior: list[float]             # length K
```

### 6.3 Pipeline CLI

```
vlens data fetch     --config configs/smoke.yaml
vlens surface fit    --symbol SPY --date 2024-12-31
vlens regime fit     --symbol SPY --model hmm_gaussian_k3
vlens publish        --config configs/smoke.yaml --out pipeline/artifacts/
vlens publish upload --bundle pipeline/artifacts/2024-12-31/  # → Vercel Blob
vlens schema export  --out web/lib/artifacts/schemas.generated.json
```

### 6.4 Web edge route contracts

```
GET /api/tickers
  -> 200 application/json
     { "tickers": ["SPY","QQQ",...], "as_of": "2024-12-31",
       "manifest_version": "2024-12-31T00:00:00Z" }

GET /api/snapshot?symbol=SPY&date=2024-12-31&view=surface|skew|term|regime
  -> 200 application/json (zod-validated against §7 schema)
  -> 304 with strong ETag
  Cache-Control: public, s-maxage=86400, stale-while-revalidate=604800
```

The web app **never** calls a paid data API at runtime. All dynamic data comes from artifacts in Vercel Blob, served behind the edge route with HTTP caching.

### 6.5 TypeScript artifact client

```ts
// web/lib/artifacts/client.ts
export async function fetchSnapshot(
  symbol: string,
  date: string,            // YYYY-MM-DD or "latest"
  view: SnapshotView,
  opts?: { signal?: AbortSignal }
): Promise<Snapshot>;      // throws ZodError on schema mismatch

export async function listTickers(): Promise<TickerIndex>;
```

---

## 7. Artifact Bundle (the wire format)

The artifact bundle is the **only** contract between the pipeline and the website. Everything else is implementation detail.

### 7.1 Layout (one bundle per pipeline run)

```
<bundle_root>/
  manifest.json
  index.json                       # ticker list + per-ticker latest date
  tickers/
    SPY/
      latest.json                  # symlink-equivalent pointer to dated file
      2024-12-31/
        surface.json               # SurfaceSnapshot
        skew.json                  # time-series of skew metrics (last N days)
        term.json                  # time-series of ATM term structure
        regime.json                # RegimeSnapshot
        meta.json                  # produced_at, pipeline_git_sha, inputs_hash
    QQQ/
      ...
  schemas/
    snapshot.schema.json           # JSON Schema (also imported by zod codegen)
```

### 7.2 Versioning

- `manifest.json.schema_version = "1.0"`. Breaking changes require an ADR and a major bump.
- Old bundles remain readable for ≥ 90 days; the web app declares the **minimum supported schema version** in `web/lib/artifacts/schemas.ts` and refuses to render older bundles with a clear error.

### 7.3 Determinism

- Canonical JSON: sorted keys, `LF` line endings, fixed float precision (8 decimals), no `NaN`/`Infinity` (encoded as `null` with a sibling `quality` flag).
- `inputs_hash = sha256(canonical_json(inputs_used))`.
- Same seed + same inputs ⇒ bit-identical bundle. CI asserts this.

### 7.4 Signing

- `manifest.json.signature = HMAC_SHA256(secret, canonical_manifest_without_signature)`.
- Secret lives in `VLENS_PIPELINE_SECRET` (GitHub Actions secret + Vercel env). The web edge route verifies signatures and refuses unsigned/tampered bundles with `502`. Local dev uses a known-public dev secret committed under `pipeline/configs/dev.secret` so contributors can run end-to-end without setup.

### 7.5 Schema codegen

- `vlens schema export` writes JSON Schema files under `web/lib/artifacts/`.
- A pnpm script `pnpm gen:schemas` converts them to zod via `json-schema-to-zod`, producing `schemas.generated.ts`.
- CI fails if `schemas.generated.ts` is stale (regenerates and diffs).

---

## 8. Algorithmic Specification

### 8.1 SVI surface fit
- Per expiry slice, fit raw SVI `w(k) = a + b*(ρ*(k-m) + sqrt((k-m)^2 + σ^2))` by L-BFGS-B with parameter bounds enforcing `b ≥ 0`, `|ρ| < 1`, `σ > 0`, `a + b·σ·sqrt(1-ρ²) ≥ 0` (no-arb necessary condition).
- Initial guesses: ATM moneyness via parabolic fit; warm-start from previous day if same expiry exists.
- Post-fit checks: butterfly (convexity) per slice, calendar (monotonic total variance) across slices. Violations recorded in `SurfaceQuality`, not silently corrected.
- Interpolation onto canonical grid uses **fitted SVI**, never raw quotes — this is the no-arbitrage anchor.

### 8.2 Skew metrics
- 25-delta risk-reversal: `IV(25Δ put) − IV(25Δ call)` derived from SVI fit (delta solved numerically under Black-Scholes).
- 25-delta butterfly: `(IV(25Δ put) + IV(25Δ call))/2 − IV(ATM)`.
- ATM term slope: `IV(90d ATM) − IV(30d ATM)`.
- All metrics are functions of the **fitted** surface, with confidence flagged when input liquidity is thin.

### 8.3 Regime model
- Features: rolling 21-day realized vol, |ATM 30-day IV − realized vol|, 25Δ RR, term slope.
- Gaussian HMM with K ∈ {2, 3}, fit on a strictly past window. Forward-filter to label test days. Refit cadence: monthly.
- State labeling is **deterministic** by ranking states on unconditional mean realized vol: low → "calm", mid → "normal", high → "stress".
- Change-point baseline (`ruptures` PELT) provided for visual comparison only; not used for state labels.

### 8.4 No-lookahead contract
- Pipeline modules expose a `cutoff: date` argument; using any data with `as_of > cutoff` is a runtime error.
- Property test: shifting input series by k bars shifts every derived series by exactly k bars.

---

## 9. Visualization Specification

### 9.1 Visual design (also in `docs/visual-design.md`)
- Single design-token file `web/app/globals.css` with light + dark themes via CSS variables; respects `prefers-color-scheme` and persists override in `localStorage`.
- Color rules:
  - **Never** encode regime state with color alone — pair with hatched pattern on the ribbon, label on hover, and ARIA label.
  - Diverging palettes for skew (negative vs positive) use a colorblind-safe scheme (Okabe-Ito).
  - Surface heatmap uses perceptually uniform `viridis`-class palette.
- Typography: variable Inter, system-stack fallback; numerals are tabular for tables.

### 9.2 Chart components contract
- Every chart component accepts `{ data, isLoading, error, asOf }` and renders a stable skeleton during `isLoading` (no layout shift).
- Every chart exposes a `data-testid` and emits a `chart:hover` custom event with the hovered datum (consumed by the provenance badge).
- The 3D surface component is the only WebGL dependency; it is dynamically imported and gated behind a "Show 3D" toggle on small viewports (`< 640px`) defaulting to off.
- All charts must render meaningfully without JS (server-rendered SVG fallbacks for line/skew/term charts; the surface tab degrades to a 2D heatmap).

### 9.3 URL state
- Canonical query params: `symbol`, `date`, `view` (`surface|skew|term|regime`), `model` (`hmm2|hmm3|cp`), `theme` (`auto|light|dark`).
- Deep links restore full UI state. Invalid params produce a 404 with a friendly recovery suggestion.

### 9.4 Performance budget (per route)
| Route | LCP | TBT | Initial JS (gzip) | Notes |
|---|---|---|---|---|
| `/` | ≤ 2.0 s | ≤ 150 ms | ≤ 180 KB | Above-the-fold uses SSG snapshot |
| `/ticker/[symbol]` | ≤ 2.5 s | ≤ 200 ms | ≤ 220 KB | Surface chunk lazy on tab |
| `/methodology` | ≤ 2.0 s | ≤ 100 ms | ≤ 140 KB | MDX, no charts |

---

## 10. Vercel Deployment Contract

### 10.1 Project setup
- One Vercel project bound to the `web/` directory (`Root Directory = web`).
- `Framework Preset = Next.js`, `Node = 20.x`.
- Build command: `pnpm install --frozen-lockfile && pnpm build`.
- Install command: `corepack enable && pnpm install --frozen-lockfile`.
- Output: default (`.next`).

### 10.2 Environment variables
| Name | Scope | Purpose |
|---|---|---|
| `VLENS_BLOB_BASE_URL` | all | Public base URL for the artifact bundle on Vercel Blob |
| `VLENS_BUNDLE_VERSION` | all | Pinned bundle id (set by pipeline workflow on each publish) |
| `VLENS_PIPELINE_SECRET` | server | HMAC verification secret |
| `VLENS_DEFAULT_TICKER` | all | e.g. `SPY` |
| `VERCEL_ANALYTICS_ID` | all | Optional |

`web/lib/env.ts` validates all envs with zod at startup; missing required vars fail the build.

### 10.3 Routes & runtimes
- Static pages: `/`, `/methodology`, `/about`, `/ticker/[symbol]/[date]` — generated via `generateStaticParams` against the manifest at build time, with **ISR** (`revalidate = 3600`).
- Edge functions: `app/api/snapshot/route.ts`, `app/api/tickers/route.ts` — `runtime = 'edge'`, `dynamic = 'force-dynamic'`, `revalidate = 86400`.
- Health: `app/api/healthz/route.ts` — `runtime = 'nodejs'`.
- Headers (set in `vercel.json`): strict CSP (no `unsafe-inline`; nonces for any inline script), `Referrer-Policy: strict-origin-when-cross-origin`, `X-Content-Type-Options: nosniff`, `Permissions-Policy` denying camera/mic/geolocation, HSTS 1 year.

### 10.4 Publish workflow (CI → Vercel)
1. GitHub Action `pipeline.yml` runs nightly + on `workflow_dispatch`:
   - `uv sync && vlens publish --config configs/full.yaml --out artifacts/<date>/`
   - `vlens publish upload --bundle artifacts/<date>/` → uploads to Vercel Blob, returns a content-addressed URL.
   - Sets `VLENS_BUNDLE_VERSION` on the Vercel project via the Vercel API.
   - Triggers a redeploy of the web project (so ISR keys + sitemap refresh).
2. On every PR, `e2e.yml` deploys a Vercel preview against the *previous good bundle* and runs Playwright. Bundle changes are gated separately so a broken pipeline never blocks a UI PR.

### 10.5 Rollback
- Bundles are immutable and content-addressed. Rollback = setting `VLENS_BUNDLE_VERSION` to a prior value and redeploying. Documented in `docs/runbook.md`.

---

## 11. Phased Execution Plan

Each phase ends with: tests green, lint/type green, docs updated, ADRs filed, `make smoke` passes, Vercel preview deploy green.

### Phase 0 — Scaffolding
- Root `Makefile`, `pnpm-workspace.yaml`, `.python-version`, `.nvmrc`, pre-commit, CI skeleton.
- Empty `pipeline/` (uv project) and `web/` (Next.js 14 App Router) importable.
- ADR 0001 (Next.js App Router), 0002 (Vercel as target).

### Phase 1 — Synthetic data + schemas
- SVI-based synthetic option-chain generator; deterministic.
- pydantic schemas for `OptionQuote`, `IVPoint`, `SurfaceSnapshot`, `RegimeSnapshot`.
- `vlens schema export` produces JSON Schema; pnpm `gen:schemas` produces zod.
- Tests: schema round-trip, determinism.

### Phase 2 — Surface fit
- SVI per-slice fit, no-arb checks, canonical grid interpolation.
- Property tests: butterfly/calendar flagged on injected violations.
- ADR 0006 (SVI parameterization).

### Phase 3 — Skew & term metrics
- 25Δ RR, 25Δ BF, ATM term slope, time-series builder.
- Tests: monotonic time index, no look-ahead.

### Phase 4 — Regime model
- Gaussian HMM (K=2, K=3), change-point baseline.
- Deterministic state labeling.
- ADR 0005 (HMM choice).

### Phase 5 — Publish & sign
- Artifact bundle builder, canonical JSON, HMAC signing, manifest.
- Local Vercel-Blob mock for dev; real upload behind env flag.
- CI asserts bit-identical bundle for fixed seed.

### Phase 6 — Web shell
- Layout, theme, header/footer, methodology MDX route.
- `lib/env.ts`, `lib/artifacts/client.ts` with zod validation.
- Lighthouse budget enforced in CI for `/` and `/methodology`.

### Phase 7 — Charts (2D)
- `RegimeRibbon`, `SkewChart`, `TermStructure`, `PriceWithRegime` with SSR fallback.
- Provenance badge wired to `chart:hover`.
- E2E: home renders with synthetic bundle, deep links work.

### Phase 8 — 3D surface
- `Surface3D` with react-three-fiber, lazy-loaded, mobile-gated.
- Accessibility: keyboard rotate, ARIA labels, reduced-motion fallback to 2D heatmap.
- ADR 0004 (r3f vs Plotly).

### Phase 9 — Edge routes & ISR
- `/api/snapshot`, `/api/tickers` on Edge with strong ETags.
- `generateStaticParams` against manifest; ISR revalidation.
- CSP + security headers in `vercel.json`.

### Phase 10 — Vercel publish pipeline
- `pipeline.yml` workflow, Vercel API integration, bundle promotion + redeploy.
- Rollback runbook.
- ADR 0003 (artifact-driven vs live API).

### Phase 11 — Hardening
- Playwright matrix (Chromium, WebKit, mobile viewport).
- Lighthouse CI gating.
- Bundle-size budget in CI (`@next/bundle-analyzer` + size-limit).
- Final docs pass.

---

## 12. Configuration Surface (`pipeline/configs/default.yaml`, excerpt)

```yaml
seed: 42

universe:
  tickers: [SPY, QQQ, IWM, AAPL, MSFT, NVDA, AMZN, GOOGL, META, TSLA]

data:
  source: synthetic           # synthetic | yfinance | csv
  start: 2019-01-01
  end:   2024-12-31

surface:
  moneyness_grid: [-0.30, -0.20, -0.10, -0.05, 0.0, 0.05, 0.10, 0.20, 0.30]
  tenor_grid_days: [7, 14, 30, 60, 90, 180, 365]
  svi:
    init: warm_start
    bounds:
      b_min: 0.0
      sigma_min: 1.0e-4
    arb_check: strict          # strict | warn

regime:
  model: hmm_gaussian_k3
  features: [rv_21, iv_minus_rv, rr_25d, term_slope]
  refit_cadence: monthly
  fit_window_years: 5

publish:
  bundle_root: pipeline/artifacts
  signing:
    secret_env: VLENS_PIPELINE_SECRET
  upload:
    target: vercel_blob        # vercel_blob | none
```

---

## 13. Testing Strategy

### 13.1 Pipeline (Python)
- **Unit:** every module in `pipeline/src/vlens/` has a paired `tests/unit/test_*.py`.
- **Property (hypothesis):** no-lookahead, monotonic time, deterministic-with-seed, SVI fit invariants on synthetic surfaces.
- **Integration:** `vlens publish --config configs/smoke.yaml` produces a bundle that validates against the JSON Schema and whose manifest verifies under HMAC.
- **Determinism:** CI runs the smoke pipeline twice and diffs SHA-256 of every JSON file.

### 13.2 Web (TypeScript)
- **Unit (vitest):** `lib/artifacts/`, `lib/url-state.ts`, env validation, schema parsing.
- **Component (RTL):** every chart with a fixed prop snapshot; loading/error/empty states.
- **E2E (Playwright):** home renders, ticker switch updates surface, deep link restores state, "Get data" downloads valid JSON, edge route returns 304 on conditional GET.
- **Lighthouse CI:** budgets in §9.4 enforced as PR check.
- **Accessibility:** `axe-core` via Playwright on every route; zero serious violations.

### 13.3 End-to-end (cross-stack)
- A single CI job runs `vlens publish --config configs/smoke.yaml`, copies the bundle to `web/public/_smoke_bundle/`, and runs the Playwright suite against `next start` pointed at that bundle. This is the integration contract.

---

## 14. Bias / Honesty Checklist (`BIAS_CHECKLIST.md`)

- No look-ahead: regime fit uses only `t-1` and earlier; SVI fit on day `t` uses only quotes timestamped `≤ t`.
- No survivorship: ticker universe is documented as point-in-time; if a ticker delists, the site shows it as "discontinued" rather than silently dropping.
- No paid-data leakage: default config + CI runs are 100 % synthetic; real-data adapters are gated and clearly labeled in the UI ("Source: synthetic demo data").
- No silent imputation: every interpolated cell is flagged in `SurfaceQuality` and rendered with a distinct hatched pattern.
- No misleading visuals: dual-axis charts forbidden; truncated y-axes always annotated; regime colors paired with patterns and labels.

---

## 15. Operating Instructions for the Implementing Agent

1. Treat this document as the contract. If a requirement here conflicts with convenience, follow this document and open an ADR.
2. Build in the order of §11. Do not advance to the next phase with red tests, failing types, or a broken Vercel preview.
3. Never introduce a feature without a test. Never ship a chart without an SSR fallback or an accessibility check.
4. Never call a paid API at request time from the web app. The artifact bundle is the contract.
5. Keep the smoke path deterministic and CPU-only. Optimize later, correctly first.
6. Prefer small, composable components. Co-locate tests with the code they exercise where the framework allows.
7. When in doubt about a financial convention, document the assumption in `docs/methodology.md` and pin it with a unit test.
8. When in doubt about a UI choice, document the rationale in `docs/visual-design.md` and add an `axe` check.

---

## 16. Interview Signal This Repo Must Broadcast

- **Quant depth:** correct SVI fit, honest no-arb checks, no-lookahead regime modeling.
- **Engineering maturity:** typed contracts across Python ↔ TypeScript via codegen, signed immutable artifacts, deterministic builds, strict CI gates.
- **Product instinct:** the deliverable is a *URL a recruiter can open on their phone* — fast, accessible, defensible, with provenance on every datum.
- **Web craft:** App Router + Edge + ISR used for the right reasons; performance, accessibility, and security budgets enforced as CI gates, not aspirations.
- **Operational maturity:** documented rollback, signed bundles, preview-per-PR, public live URL.
