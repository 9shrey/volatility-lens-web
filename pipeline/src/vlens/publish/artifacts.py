"""Build & write the artifact bundle."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from ..config.schema import RunConfig
from ..data.schemas import (
    IVPoint,
    Manifest,
    RegimeSnapshot,
    SkewMetric,
    SurfaceSnapshot,
    TermPoint,
    TickerIndex,
    TickerIndexEntry,
)
from ..data.synthetic import generate_path
from ..regime.hmm import fit_predict_hmm
from ..regime.labels import build_features
from ..skew.series import daily_skew_series, daily_term_structure
from ..surface.interpolate import build_surface
from ..utils.hashing import canonical_json_bytes, hmac_sign, sha256_hex
from ..utils.io import write_json
from ..utils.logging import get_logger

LOG = get_logger("vlens.publish")
SCHEMA_VERSION = "1.0"


def _git_sha() -> str:
    return os.environ.get("VLENS_PIPELINE_GIT_SHA", "unknown")


def _produced_at() -> datetime:
    """Wall-clock UTC, second-precision; overridable via env for deterministic builds."""
    override = os.environ.get("VLENS_PRODUCED_AT")
    if override:
        ts = datetime.fromisoformat(override)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=UTC)
        return ts.astimezone(UTC).replace(microsecond=0)
    return datetime.now(UTC).replace(microsecond=0)


def _resolve_secret(env_name: str) -> str:
    """Return signing secret. Falls back to a deterministic dev secret so
    the smoke path is fully reproducible without secrets configured."""
    return os.environ.get(env_name) or "dev-secret-do-not-use-in-prod"


def _quotes_from_synthetic(
    path,
    moneyness_grid: list[float],
) -> list[dict[float, list[IVPoint]]]:
    """For each date, build a per-tenor dict of IVPoints from the synthetic surface."""
    out: list[dict[float, list[IVPoint]]] = []
    for i in range(len(path.dates)):
        per_tenor: dict[float, list[IVPoint]] = {}
        surf = path.surfaces[i]
        for j, ty in enumerate(path.tenor_grid_years):
            pts = [
                IVPoint(
                    log_moneyness=float(k),
                    tenor_years=float(ty),
                    iv=float(surf[j, ki]),
                    weight=1.0,
                )
                for ki, k in enumerate(moneyness_grid)
            ]
            per_tenor[float(ty)] = pts
        out.append(per_tenor)
    return out


def build_for_ticker(
    *,
    symbol: str,
    cfg: RunConfig,
) -> tuple[
    list[SurfaceSnapshot],
    list[SkewMetric],
    list[TermPoint],
    RegimeSnapshot,
]:
    """Run the full per-ticker pipeline (synthetic-only path for now)."""
    if cfg.data.source != "synthetic":
        raise NotImplementedError(f"data.source={cfg.data.source!r} not supported in this build")

    path = generate_path(
        symbol=symbol,
        start=cfg.data.start,
        end=cfg.data.end,
        moneyness_grid=cfg.surface.moneyness_grid,
        tenor_grid_days=cfg.surface.tenor_grid_days,
        seed=cfg.seed,
    )

    quotes_per_day = _quotes_from_synthetic(path, cfg.surface.moneyness_grid)

    snapshots: list[SurfaceSnapshot] = []
    for i, d in enumerate(path.dates):
        snap = build_surface(
            symbol=symbol,
            as_of=d,
            points_by_tenor=quotes_per_day[i],
            moneyness_grid=cfg.surface.moneyness_grid,
            tenor_days=cfg.surface.tenor_grid_days,
            b_min=cfg.surface.svi.bounds.b_min,
            sigma_min=cfg.surface.svi.bounds.sigma_min,
        )
        snapshots.append(snap)

    skew = daily_skew_series(snapshots)
    term = daily_term_structure(snapshots, cfg.surface.tenor_grid_days)

    rv_lookup = {d: float(path.realized_vol_21d[i]) for i, d in enumerate(path.dates)}
    feat_dates, feat = build_features(skew, rv_lookup)
    n_states_param = 3 if cfg.regime.model == "hmm_gaussian_k3" else 2
    regime = fit_predict_hmm(
        symbol=symbol,
        dates=feat_dates,
        features=feat,
        n_states=n_states_param,  # type: ignore[arg-type]
        seed=cfg.seed,
    )
    return snapshots, skew, term, regime


def write_bundle(
    *,
    out_root: Path,
    cfg: RunConfig,
) -> Path:
    """Run the pipeline for every ticker in ``cfg.universe`` and write a bundle."""
    out_root.mkdir(parents=True, exist_ok=True)
    produced_at = _produced_at()

    inputs_repr = cfg.model_dump(mode="json")
    inputs_hash = sha256_hex(canonical_json_bytes(inputs_repr))

    index_entries: list[TickerIndexEntry] = []
    bundle_files: list[Path] = []

    for symbol in cfg.universe.tickers:
        LOG.info("building ticker %s", symbol)
        snapshots, skew, term, regime = build_for_ticker(symbol=symbol, cfg=cfg)
        if not snapshots:
            continue
        latest = snapshots[-1]
        latest_dir = out_root / "tickers" / symbol / latest.as_of.isoformat()

        # surface snapshot for latest
        surface_path = latest_dir / "surface.json"
        write_json(surface_path, latest.model_dump(mode="json"))
        bundle_files.append(surface_path)

        # skew + term + regime full series (latest = same file path)
        skew_path = latest_dir / "skew.json"
        write_json(skew_path, [s.model_dump(mode="json") for s in skew])
        bundle_files.append(skew_path)

        term_path = latest_dir / "term.json"
        write_json(term_path, [t.model_dump(mode="json") for t in term])
        bundle_files.append(term_path)

        regime_path = latest_dir / "regime.json"
        write_json(regime_path, regime.model_dump(mode="json"))
        bundle_files.append(regime_path)

        # meta
        meta_path = latest_dir / "meta.json"
        meta = {
            "produced_at": produced_at.isoformat(),
            "pipeline_git_sha": _git_sha(),
            "inputs_hash": inputs_hash,
            "symbol": symbol,
            "as_of": latest.as_of.isoformat(),
        }
        write_json(meta_path, meta)
        bundle_files.append(meta_path)

        # latest pointer
        latest_pointer = out_root / "tickers" / symbol / "latest.json"
        write_json(latest_pointer, {"path": latest.as_of.isoformat()})
        bundle_files.append(latest_pointer)

        index_entries.append(
            TickerIndexEntry(symbol=symbol, latest_date=latest.as_of, n_dates=len(snapshots))
        )

    # index
    if not index_entries:
        raise RuntimeError("No tickers produced any snapshots")
    bundle_id = sha256_hex(
        canonical_json_bytes({"tickers": [e.symbol for e in index_entries], "ts": produced_at.isoformat()})
    )[:16]
    index = TickerIndex(
        tickers=index_entries,
        as_of=max(e.latest_date for e in index_entries),
        manifest_version=produced_at.isoformat(),
    )
    index_path = out_root / "index.json"
    write_json(index_path, index.model_dump(mode="json"))
    bundle_files.append(index_path)

    # manifest (signature filled below)
    manifest_unsigned = Manifest(
        schema_version=SCHEMA_VERSION,
        pipeline_git_sha=_git_sha(),
        produced_at=produced_at,
        inputs_hash=inputs_hash,
        bundle_id=bundle_id,
    )
    manifest_dict = manifest_unsigned.model_dump(mode="json")
    secret = _resolve_secret(cfg.publish.signing.secret_env)
    sig_payload = canonical_json_bytes({k: v for k, v in manifest_dict.items() if k != "signature"})
    manifest_dict["signature"] = hmac_sign(secret, sig_payload)
    manifest_path = out_root / "manifest.json"
    write_json(manifest_path, manifest_dict)

    LOG.info("bundle written to %s (%d files, bundle_id=%s)", out_root, len(bundle_files) + 1, bundle_id)
    return out_root
