# vlens — Volatility & Regime Lens (Python pipeline)

The deterministic research pipeline that produces the JSON artifact bundle consumed by the Next.js web app.

## Install

```bash
python -m pip install -e .[dev]
```

## CLI

```bash
vlens publish --config configs/smoke.yaml --out artifacts/smoke
vlens verify  --bundle artifacts/smoke
vlens schema export --out ../web/lib/artifacts/schemas.generated.json
```

## Tests

```bash
python -m pytest -q
```

See top-level `MASTER_PROMPT.md` §6–§8 for contracts and algorithmic spec.
