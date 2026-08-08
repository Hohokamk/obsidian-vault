#!/usr/bin/env python3
"""Simple, explainable random-search baseline for binary amplitude masks.

This is intentionally not presented as an 'AI optimum'. It gives students a
repeatable baseline before adopting DEAP or pymoo.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from array_factor import PlanarArray, array_factor, normalized_power_db


def score_mask(
    array: PlanarArray,
    mask: np.ndarray,
    target_theta_deg: float,
    target_phi_deg: float,
    null_theta_deg: float | None,
    sparsity_penalty: float,
) -> tuple[float, dict[str, float]]:
    weights = mask.astype(np.complex128)
    target_field = array_factor(array, weights, target_theta_deg, target_phi_deg)
    target_power = float(np.abs(target_field) ** 2)
    null_power = 0.0
    if null_theta_deg is not None:
        null_field = array_factor(array, weights, null_theta_deg, target_phi_deg)
        null_power = float(np.abs(null_field) ** 2)
    on_ratio = float(mask.mean())
    # Normalize target by N^2 so weights and array size remain interpretable.
    normalized_target = target_power / float((array.rows * array.cols) ** 2)
    normalized_null = null_power / float((array.rows * array.cols) ** 2)
    score = normalized_target - 2.0 * normalized_null - sparsity_penalty * on_ratio
    return score, {
        "target_power_norm": normalized_target,
        "null_power_norm": normalized_null,
        "on_ratio": on_ratio,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--rows", type=int, default=16)
    p.add_argument("--cols", type=int, default=16)
    p.add_argument("--target-theta", type=float, default=0.0)
    p.add_argument("--target-phi", type=float, default=0.0)
    p.add_argument("--null-theta", type=float)
    p.add_argument("--density", type=float, default=0.5)
    p.add_argument("--trials", type=int, default=10000)
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--sparsity-penalty", type=float, default=0.02)
    p.add_argument("--out", type=Path, default=Path("best_mask.npy"))
    args = p.parse_args()

    if not 0.0 <= args.density <= 1.0:
        p.error("--density must be in [0,1]")
    array = PlanarArray(args.rows, args.cols)
    rng = np.random.default_rng(args.seed)
    best_score = -np.inf
    best_mask = None
    best_metrics = None

    for trial in range(args.trials):
        mask = (rng.random((args.rows, args.cols)) < args.density).astype(np.uint8)
        if not mask.any():
            continue
        score, metrics = score_mask(
            array,
            mask,
            args.target_theta,
            args.target_phi,
            args.null_theta,
            args.sparsity_penalty,
        )
        if score > best_score:
            best_score, best_mask, best_metrics = score, mask.copy(), metrics
        if (trial + 1) % max(1, args.trials // 10) == 0:
            print(f"trial={trial+1} best_score={best_score:.6f}")

    if best_mask is None:
        raise RuntimeError("no valid mask generated")
    np.save(args.out, best_mask)
    print(f"saved {args.out}")
    print(f"best_score={best_score:.6f}, metrics={best_metrics}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
