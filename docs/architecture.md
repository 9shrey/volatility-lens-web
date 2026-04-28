# Architecture

```
                 ┌──────────────────────────┐
   nightly job   │   pipeline/  (Python)    │
   GH Actions ──▶│   vlens publish          │
                 │   ↳ synthetic SVI        │
                 │   ↳ HMM regime           │
                 │   ↳ canonical JSON       │
                 │   ↳ HMAC signed manifest │
                 └─────────────┬────────────┘
                               │ uploads
                               ▼
                 ┌──────────────────────────┐
                 │ Vercel Blob (versioned)  │
                 │ <bundle_id>/manifest.json│
                 │ <bundle_id>/index.json   │
                 │ <bundle_id>/tickers/...  │
                 └─────────────┬────────────┘
                               │ HTTP, cached at edge
                               ▼
                 ┌──────────────────────────┐
                 │   web/  (Next.js 14)     │
                 │   ↳ SSG /, /ticker/[s]   │
                 │   ↳ Edge /api/snapshot   │
                 │   ↳ Edge /api/tickers    │
                 │   ↳ Node /api/healthz    │
                 │   ↳ ISR revalidate=3600  │
                 └─────────────┬────────────┘
                               │ HTML + JSON
                               ▼
                       (public viewer)
```

## Components

- **`pipeline/`**: deterministic Python pipeline (synthetic data path is the CI
  default). Output is an immutable, signed bundle (see `MASTER_PROMPT.md` §7).
- **`web/`**: Next.js 14 App Router. Statically generated against the manifest
  at build time, with ISR. Two edge routes serve dynamic snapshot slices.
- **`vercel.json`**: build, security headers, CSP. The web app is the deployed
  artifact; the Python pipeline never runs on Vercel itself.
- **CI** (`.github/workflows/`): `ci.yml` (lint+type+test), `pipeline.yml`
  (nightly publish), `e2e.yml` (Playwright on a fresh smoke bundle).

## No-runtime-API rule

The website **never** calls a paid data API at request time. The artifact bundle
is the contract. See [`decisions/0003-artifact-driven-vs-live-api.md`](decisions/0003-artifact-driven-vs-live-api.md).
