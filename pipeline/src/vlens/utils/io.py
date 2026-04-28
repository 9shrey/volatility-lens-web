"""I/O helpers for canonical JSON files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .hashing import canonical_json


def write_json(path: Path, obj: Any) -> str:
    """Write ``obj`` as canonical JSON; return the JSON string written."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_json(obj)
    path.write_text(payload + "\n", encoding="utf-8", newline="\n")
    return payload


def read_json(path: Path) -> Any:
    import json

    return json.loads(path.read_text(encoding="utf-8"))
