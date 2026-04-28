"""Canonical JSON + HMAC behavior."""

from __future__ import annotations

import math

import pytest

from vlens.utils.hashing import (
    canonical_json,
    canonical_json_bytes,
    hmac_sign,
    hmac_verify,
    sha256_hex,
)


def test_canonical_json_sorts_keys_and_rounds_floats() -> None:
    a = canonical_json({"b": 1.123456789012, "a": 2.0})
    b = canonical_json({"a": 2.0, "b": 1.123456789012})
    assert a == b
    assert "1.12345679" in a  # rounded to 8 decimals


def test_canonical_json_rejects_nan_inf() -> None:
    with pytest.raises(ValueError):
        canonical_json({"x": float("nan")})
    with pytest.raises(ValueError):
        canonical_json({"x": math.inf})


def test_canonical_json_uses_compact_separators() -> None:
    s = canonical_json({"a": [1, 2, 3]})
    assert s == '{"a":[1,2,3]}'


def test_sha256_hex_is_stable() -> None:
    assert sha256_hex(b"abc") == sha256_hex("abc")


def test_hmac_roundtrip() -> None:
    payload = canonical_json_bytes({"x": 1, "y": [1, 2]})
    sig = hmac_sign("secret", payload)
    assert hmac_verify("secret", payload, sig)
    assert not hmac_verify("other", payload, sig)
