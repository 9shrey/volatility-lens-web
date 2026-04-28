# Runbook

## Publish a fresh bundle

```bash
cd 15-volatility-lens-web/pipeline
export VLENS_PIPELINE_SECRET=...   # never echo
export VLENS_PIPELINE_GIT_SHA=$(git rev-parse HEAD)
export VLENS_PRODUCED_AT=$(date -u -Iseconds)
python -m vlens.cli publish --config configs/full.yaml --out artifacts/$(date +%Y-%m-%d)
python -m vlens.cli verify  --bundle artifacts/$(date +%Y-%m-%d)
python -m vlens.cli upload  --bundle artifacts/$(date +%Y-%m-%d)
```

## Promote a bundle on Vercel

1. Set `VLENS_BUNDLE_VERSION` (the content-addressed `bundle_id` from
   `manifest.json`) on the Vercel project.
2. Trigger a redeploy of the production environment so static pages and the
   sitemap re-render with the new manifest.

## Roll back

Bundles are immutable and content-addressed. To roll back:

1. Set `VLENS_BUNDLE_VERSION` to a prior known-good `bundle_id`.
2. Redeploy.
3. Open a `postmortem-*.md` issue noting which bundle was rolled back and why.

## Debug a bad artifact

- `vlens verify --bundle <path>` to confirm the manifest signature.
- `vlens schema export --out /tmp/schemas.json` and validate any failing JSON file with
  any JSON-Schema validator (e.g. `ajv-cli`).
- The web edge routes refuse unsigned/tampered bundles with HTTP 502 and surface
  the zod parse error in the JSON body.
