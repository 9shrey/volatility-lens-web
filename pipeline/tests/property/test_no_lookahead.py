"""Property: shifting the input series shifts derived series identically."""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from vlens.regime.hmm import fit_predict_hmm


@given(shift=st.integers(min_value=1, max_value=5))
@settings(deadline=None, max_examples=5)
def test_hmm_state_assignment_shift_equivariant(shift: int) -> None:
    """Shifting the date axis by `k` days shifts every derived state by exactly k days."""
    g = np.random.default_rng(123)
    n = 80
    half = n // 2
    rv = np.concatenate([g.normal(0.10, 0.01, half), g.normal(0.30, 0.02, n - half)])
    feats = np.stack([rv, g.normal(0, 0.005, n), g.normal(0, 0.005, n), g.normal(0, 0.005, n)], axis=1)
    d0 = [date(2024, 1, 1) + timedelta(days=i) for i in range(n)]
    d1 = [d + timedelta(days=shift) for d in d0]

    a = fit_predict_hmm(symbol="X", dates=d0, features=feats, n_states=2, seed=42)
    b = fit_predict_hmm(symbol="X", dates=d1, features=feats, n_states=2, seed=42)

    sa = [r.state for r in a.states]
    sb = [r.state for r in b.states]
    assert sa == sb  # state labels are functions of features, not dates
    # date alignment shifted by exactly `shift`
    for ra, rb in zip(a.states, b.states):
        assert (rb.date - ra.date).days == shift
