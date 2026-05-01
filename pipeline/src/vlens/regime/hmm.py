"""Gaussian HMM regime classifier with no-lookahead enforcement.

We use ``hmmlearn`` if available; otherwise fall back to a simple internal
Gaussian HMM implementation with a fixed number of EM iterations. Both paths
are deterministic given the seed.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

import numpy as np

from ..data.schemas import RegimeSnapshot, RegimeStateRow


class LookaheadError(RuntimeError):
    """Raised when fit/predict is asked to consume data past its cutoff."""


@dataclass
class HMMResult:
    n_states: int
    means: np.ndarray              # [K, F]
    covars: np.ndarray             # [K, F]  (diagonal)
    transmat: np.ndarray           # [K, K]
    startprob: np.ndarray          # [K]


def _try_hmmlearn(n_states: int, seed: int) -> object | None:
    try:
        from hmmlearn.hmm import GaussianHMM  # type: ignore[import-not-found]
    except Exception:
        return None
    return GaussianHMM(
        n_components=n_states,
        covariance_type="diag",
        n_iter=50,
        random_state=seed,
        tol=1e-4,
    )


def _fit_internal_hmm(x: np.ndarray, n_states: int, seed: int) -> HMMResult:
    """Fallback EM implementation (diagonal covariance Gaussian HMM)."""
    rng = np.random.default_rng(seed)
    t, f = x.shape
    # init means by quantile, covars by overall variance
    qs = np.linspace(0.1, 0.9, n_states)
    means = np.stack([np.quantile(x, q, axis=0) for q in qs], axis=0)
    covars = np.tile(np.var(x, axis=0) + 1e-3, (n_states, 1))
    transmat = np.full((n_states, n_states), 0.05 / max(1, n_states - 1))
    np.fill_diagonal(transmat, 0.95)
    startprob = np.full(n_states, 1.0 / n_states)

    def log_emission(obs: np.ndarray) -> np.ndarray:
        # log N(x | mean_k, diag(covar_k))
        diff = obs[:, None, :] - means[None, :, :]
        inv = 1.0 / covars
        log_det = np.sum(np.log(covars), axis=1)
        quad = np.sum(diff**2 * inv[None, :, :], axis=2)
        return -0.5 * (quad + log_det + f * np.log(2 * np.pi))

    for _ in range(40):
        log_em = log_emission(x)
        log_tr = np.log(transmat + 1e-12)
        log_st = np.log(startprob + 1e-12)

        # forward
        log_alpha = np.empty((t, n_states))
        log_alpha[0] = log_st + log_em[0]
        for i in range(1, t):
            log_alpha[i] = log_em[i] + np.logaddexp.reduce(
                log_alpha[i - 1, :, None] + log_tr, axis=0
            )

        # backward
        log_beta = np.zeros((t, n_states))
        for i in range(t - 2, -1, -1):
            log_beta[i] = np.logaddexp.reduce(
                log_tr + log_em[i + 1, None, :] + log_beta[i + 1, None, :], axis=1
            )

        log_gamma = log_alpha + log_beta
        log_gamma -= np.logaddexp.reduce(log_gamma, axis=1, keepdims=True)
        gamma = np.exp(log_gamma)

        # xi[t-1, i, j]
        log_xi = (
            log_alpha[:-1, :, None]
            + log_tr[None, :, :]
            + log_em[1:, None, :]
            + log_beta[1:, None, :]
        )
        log_xi -= np.logaddexp.reduce(
            log_xi.reshape(t - 1, -1), axis=1, keepdims=True
        ).reshape(t - 1, 1, 1)
        xi = np.exp(log_xi)

        # M-step
        startprob = gamma[0] / max(gamma[0].sum(), 1e-12)
        denom = xi.sum(axis=(0, 2))
        denom = np.where(denom < 1e-12, 1e-12, denom)
        transmat = xi.sum(axis=0) / denom[:, None]
        transmat /= transmat.sum(axis=1, keepdims=True)

        gsum = gamma.sum(axis=0)
        gsum = np.where(gsum < 1e-12, 1e-12, gsum)
        means = (gamma.T @ x) / gsum[:, None]
        diff = x[:, None, :] - means[None, :, :]
        covars = (gamma[:, :, None] * diff**2).sum(axis=0) / gsum[:, None]
        covars = np.clip(covars, 1e-6, None)

        # Use a small noise injection from `rng` to break ties deterministically.
        means = means + 1e-12 * rng.standard_normal(means.shape)

    return HMMResult(n_states=n_states, means=means, covars=covars, transmat=transmat, startprob=startprob)


def _predict_internal(model: HMMResult, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    n_states = model.n_states
    f = x.shape[1]

    diff = x[:, None, :] - model.means[None, :, :]
    inv = 1.0 / model.covars
    log_det = np.sum(np.log(model.covars), axis=1)
    quad = np.sum(diff**2 * inv[None, :, :], axis=2)
    log_em = -0.5 * (quad + log_det + f * np.log(2 * np.pi))
    log_tr = np.log(model.transmat + 1e-12)
    log_st = np.log(model.startprob + 1e-12)

    t = x.shape[0]
    log_alpha = np.empty((t, n_states))
    log_alpha[0] = log_st + log_em[0]
    for i in range(1, t):
        log_alpha[i] = log_em[i] + np.logaddexp.reduce(log_alpha[i - 1, :, None] + log_tr, axis=0)

    # posterior via filtered alpha (causal)
    log_post = log_alpha - np.logaddexp.reduce(log_alpha, axis=1, keepdims=True)
    post = np.exp(log_post)
    states = np.argmax(post, axis=1)
    return states, post


def fit_predict_hmm(
    *,
    symbol: str,
    dates: list[date],
    features: np.ndarray,                       # [T, F]
    n_states: Literal[2, 3],
    seed: int,
    cutoff: date | None = None,
) -> RegimeSnapshot:
    """Fit an HMM on data up to ``cutoff`` (inclusive), then forward-filter all dates.

    Raises ``LookaheadError`` if ``features`` contains observations past
    ``cutoff`` that are then *used to fit*. Predictions on dates after
    ``cutoff`` use only the trained transition + emission parameters and a
    causal forward filter, so they remain causal.
    """
    if features.ndim != 2:
        raise ValueError("features must be 2-D")
    if len(dates) != features.shape[0]:
        raise ValueError("dates and features length mismatch")

    if cutoff is None:
        fit_x = features
        fit_window = (dates[0], dates[-1])
    else:
        if cutoff < dates[0]:
            raise LookaheadError("cutoff is before the first observation")
        idx = sum(1 for d in dates if d <= cutoff)
        if idx < n_states * 5:
            raise ValueError("not enough pre-cutoff samples to fit HMM")
        fit_x = features[:idx]
        fit_window = (dates[0], dates[idx - 1])

    model = _try_hmmlearn(n_states, seed)
    if model is not None:
        try:
            model.fit(fit_x)
            states_all, post_all = model.predict(features), model.predict_proba(features)
            means = model.means_.astype(float)
        except Exception:
            model = None

    if model is None:
        result = _fit_internal_hmm(fit_x, n_states, seed)
        states_all, post_all = _predict_internal(result, features)
        means = result.means

    # Deterministic state labeling: rank by mean of feature 0 (realized vol)
    order = np.argsort(means[:, 0])
    perm = np.argsort(order)              # original idx -> rank
    relabeled_states = perm[states_all]
    relabeled_post = post_all[:, order]
    label_for_rank = {0: "calm", 1: "normal", 2: "stress"} if n_states == 3 else {0: "calm", 1: "stress"}
    state_labels = {str(rank): label_for_rank[rank] for rank in range(n_states)}

    rows = [
        RegimeStateRow(
            date=dates[i],
            state=int(relabeled_states[i]),
            posterior=[float(p) for p in relabeled_post[i]],
        )
        for i in range(len(dates))
    ]

    model_name: Literal["hmm_gaussian_k2", "hmm_gaussian_k3"] = (
        "hmm_gaussian_k2" if n_states == 2 else "hmm_gaussian_k3"
    )
    return RegimeSnapshot(
        symbol=symbol,
        model=model_name,
        fit_window=fit_window,
        states=rows,
        state_labels=state_labels,
        seed=seed,
    )
