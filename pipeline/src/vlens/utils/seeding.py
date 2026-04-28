"""Deterministic seeding helpers."""

from __future__ import annotations

import os
import random

import numpy as np


def set_global_seed(seed: int) -> None:
    """Seed Python ``random``, NumPy, and the ``PYTHONHASHSEED`` env var."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)


def rng(seed: int) -> np.random.Generator:
    """Return a fresh, isolated NumPy ``Generator`` for the given seed."""
    return np.random.default_rng(seed)
