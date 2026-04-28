"""Canonical JSON serialization, hashing, and HMAC signing.

The entire artifact bundle's reproducibility hinges on this module:

* keys are sorted
* line endings are LF
* floats are rounded to a fixed number of decimals
* NaN/Infinity are rejected (must be encoded as ``null`` upstream)
"""

from __future__ import annotations

import hashlib
import hmac
import json
import math
from typing import Any

FLOAT_PRECISION = 8


def _round_floats(obj: Any) -> Any:
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            raise ValueError("NaN/Infinity not allowed in canonical JSON; encode as null upstream")
        return round(obj, FLOAT_PRECISION)
    if isinstance(obj, dict):
        return {k: _round_floats(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_round_floats(v) for v in obj]
    return obj


def canonical_json(obj: Any) -> str:
    """Return canonical JSON: sorted keys, LF, fixed float precision, no NaN."""
    rounded = _round_floats(obj)
    return json.dumps(
        rounded,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    )


def canonical_json_bytes(obj: Any) -> bytes:
    return canonical_json(obj).encode("utf-8")


def sha256_hex(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def hmac_sign(secret: str | bytes, payload: bytes) -> str:
    """HMAC-SHA256 hex digest of ``payload`` using ``secret``."""
    if isinstance(secret, str):
        secret = secret.encode("utf-8")
    return hmac.new(secret, payload, hashlib.sha256).hexdigest()


def hmac_verify(secret: str | bytes, payload: bytes, signature: str) -> bool:
    expected = hmac_sign(secret, payload)
    return hmac.compare_digest(expected, signature)
