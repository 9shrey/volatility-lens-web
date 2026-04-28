"""Vercel Blob upload (no-op stub by default).

In production, set ``VLENS_BLOB_RW_TOKEN`` and call ``upload_bundle``; this
stub keeps the public CLI happy in CI / local dev where Blob is not configured.
"""

from __future__ import annotations

import os
from pathlib import Path

from ..utils.logging import get_logger

LOG = get_logger("vlens.publish.upload")


def upload_bundle(bundle_root: Path, *, base_url_env: str = "VLENS_BLOB_BASE_URL") -> str:
    token = os.environ.get("VLENS_BLOB_RW_TOKEN")
    base = os.environ.get(base_url_env)
    if not token or not base:
        LOG.info("VLENS_BLOB_RW_TOKEN/%s missing — skipping upload (dev/CI)", base_url_env)
        return f"local://{bundle_root}"
    raise NotImplementedError(
        "Real Vercel Blob upload not wired in this build; stubbed for safety."
    )
