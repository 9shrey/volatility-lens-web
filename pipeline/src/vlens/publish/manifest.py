"""Manifest verification (HMAC + schema_version)."""

from __future__ import annotations

import os
from pathlib import Path

from ..utils.hashing import canonical_json_bytes, hmac_verify
from ..utils.io import read_json


class ManifestError(RuntimeError):
    pass


def verify_bundle(bundle_root: Path, *, secret_env: str = "VLENS_PIPELINE_SECRET") -> dict:
    manifest_path = bundle_root / "manifest.json"
    if not manifest_path.exists():
        raise ManifestError(f"manifest.json not found at {manifest_path}")
    manifest = read_json(manifest_path)
    if "signature" not in manifest or not manifest["signature"]:
        raise ManifestError("manifest is unsigned")
    sig = manifest["signature"]
    payload = canonical_json_bytes({k: v for k, v in manifest.items() if k != "signature"})
    secret = os.environ.get(secret_env) or "dev-secret-do-not-use-in-prod"
    if not hmac_verify(secret, payload, sig):
        raise ManifestError("HMAC signature mismatch")
    if manifest.get("schema_version") != "1.0":
        raise ManifestError(f"unsupported schema_version {manifest.get('schema_version')!r}")
    return manifest
