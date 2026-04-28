# Vercel environment variables

Configure these in the Vercel project (Settings → Environment Variables).

| Name                    | Scope          | Purpose                                                       |
|-------------------------|----------------|---------------------------------------------------------------|
| `VLENS_BLOB_BASE_URL`   | All            | Public base URL for the artifact bundle on Vercel Blob.       |
| `VLENS_BUNDLE_VERSION`  | All            | Pinned bundle id; updated by the nightly pipeline workflow.   |
| `VLENS_PIPELINE_SECRET` | Server only    | HMAC verification secret for manifest signatures.             |
| `VLENS_DEFAULT_TICKER`  | All            | E.g. `SPY`. Drives the landing page.                          |
| `VERCEL_ANALYTICS_ID`   | All (optional) | Vercel Analytics ID.                                          |

The web app calls `env()` once at startup; missing required vars **fail the build**.
