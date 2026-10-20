#!/usr/bin/env python3
"""Generate baseline continuous, one-bit phase, and amplitude-mask cuts."""

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

from array_factor import (
    PlanarArray,
    amplitude_mask,
    beamwidth_3db,
    cut,
    main_lobe_angle,
    peak_sidelobe_level,
    quantize_one_bit,
    save_cut_csv,
    steering_weights,
)


def describe(name, theta, db):
    strongest = np.argsort(db)[-8:][::-1]
    separated = []
    for index in strongest:
        angle = float(theta[index])
        if all(abs(angle - existing) > 3.0 for existing in separated):
            separated.append(angle)
        if len(separated) == 2:
            break
    print(
        f"{name}: first_global_max={main_lobe_angle(theta, db):.2f} deg, "
        f"strong_peak_angles={separated}, BW3dB={beamwidth_3db(theta, db)}, "
        f"PSLL~={peak_sidelobe_level(theta, db):.2f} dB"
    )


def main() -> int:
    out = Path("simulation_results")
    out.mkdir(exist_ok=True)
    array = PlanarArray(16, 16, 0.5, 0.5)
    target_theta = 25.0
    target_phi = 0.0

    continuous = steering_weights(array, target_theta, target_phi)
    one_bit = quantize_one_bit(continuous)
    rng = np.random.default_rng(2026)
    mask = amplitude_mask((rng.random((16, 16)) < 0.5).astype(np.uint8))

    results = []
    for name, weights in [
        ("continuous", continuous),
        ("one_bit", one_bit),
        ("amplitude_mask", mask),
    ]:
        theta, db = cut(array, weights, phi_deg=target_phi)
        results.append((name, theta, db))
        save_cut_csv(out / f"{name}.csv", theta, db)
        describe(name, theta, db)

    plt.figure(figsize=(8, 5))
    for name, theta, db in results:
        plt.plot(theta, db, label=name)
    plt.ylim(-50, 1)
    plt.xlim(-90, 90)
    plt.xlabel("Signed theta (deg)")
    plt.ylabel("Normalized power (dB)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "cuts.png", dpi=180)
    print("Note: ideal +/-1 real weights may create equal symmetric twin beams in this simple model.")
    print(f"saved to {out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
