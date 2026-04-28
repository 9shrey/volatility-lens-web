"""Shared fixtures and path setup."""

from __future__ import annotations

import sys
from pathlib import Path

# Make the src/ layout importable when running pytest without an editable install.
_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
