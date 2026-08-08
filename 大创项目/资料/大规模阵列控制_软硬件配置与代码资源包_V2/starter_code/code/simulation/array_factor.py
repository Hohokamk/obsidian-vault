"""Planar-array factor utilities with explicit coordinate conventions.

Convention:
- Array lies in the x-y plane.
- theta is measured from +z, phi is the azimuth from +x toward +y.
- Complex field uses exp(+j k r dot u). Steering weights therefore use
  exp(-j k r dot u_target).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True, slots=True)
class PlanarArray:
    rows: int
    cols: int
    dx_lambda: float = 0.5
    dy_lambda: float = 0.5

    def positions_lambda(self, centered: bool = True) -> np.ndarray:
        """Return shape (rows, cols, 3), in wavelengths."""
        x = np.arange(self.cols, dtype=float) * self.dx_lambda
        y = np.arange(self.rows, dtype=float) * self.dy_lambda
        if centered:
            x -= x.mean()
            y -= y.mean()
        xx, yy = np.meshgrid(x, y)
        return np.stack((xx, yy, np.zeros_like(xx)), axis=-1)


def direction_vector(theta_deg, phi_deg) -> np.ndarray:
    theta = np.deg2rad(np.asarray(theta_deg, dtype=float))
    phi = np.deg2rad(np.asarray(phi_deg, dtype=float))
    return np.stack(
        (
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta),
        ),
        axis=-1,
    )


def steering_weights(
    array: PlanarArray,
    theta_deg: float,
    phi_deg: float,
) -> np.ndarray:
    positions = array.positions_lambda()
    u0 = direction_vector(theta_deg, phi_deg)
    phase = -2.0 * np.pi * np.einsum("...k,k->...", positions, u0)
    return np.exp(1j * phase)


def quantize_one_bit(weights: np.ndarray) -> np.ndarray:
    """Quantize arbitrary complex weights to ideal states {+1, -1}."""
    phase = np.angle(weights)
    return np.where(np.cos(phase) >= 0.0, 1.0 + 0j, -1.0 + 0j)


def amplitude_mask(mask: np.ndarray) -> np.ndarray:
    mask = np.asarray(mask)
    if np.any((mask != 0) & (mask != 1)):
        raise ValueError("amplitude mask must contain only 0/1")
    return mask.astype(np.complex128)


def array_factor(
    array: PlanarArray,
    weights: np.ndarray,
    theta_deg,
    phi_deg,
) -> np.ndarray:
    """Return complex array factor on broadcastable theta/phi grids."""
    weights = np.asarray(weights, dtype=np.complex128)
    if weights.shape != (array.rows, array.cols):
        raise ValueError(f"weights must have shape {(array.rows, array.cols)}")
    positions = array.positions_lambda().reshape(-1, 3)
    flat_weights = weights.reshape(-1)
    theta, phi = np.broadcast_arrays(
        np.asarray(theta_deg, dtype=float), np.asarray(phi_deg, dtype=float)
    )
    u = direction_vector(theta, phi)
    phase = 2.0 * np.pi * np.einsum("nk,...k->...n", positions, u)
    return np.einsum("n,...n->...", flat_weights, np.exp(1j * phase))


def normalized_power_db(field: np.ndarray, floor_db: float = -80.0) -> np.ndarray:
    power = np.abs(field) ** 2
    maximum = float(np.max(power))
    if maximum <= 0.0:
        return np.full_like(power, floor_db, dtype=float)
    normalized = np.maximum(power / maximum, 10.0 ** (floor_db / 10.0))
    return 10.0 * np.log10(normalized)


def cut(
    array: PlanarArray,
    weights: np.ndarray,
    phi_deg: float = 0.0,
    theta_min: float = -90.0,
    theta_max: float = 90.0,
    points: int = 1801,
) -> tuple[np.ndarray, np.ndarray]:
    """Return a signed-theta principal-plane cut.

    Negative theta is represented by using abs(theta) and adding 180 degrees
    to phi. This makes a convenient -90..90 plot while keeping the standard
    0..180 polar-angle convention internally.
    """
    signed_theta = np.linspace(theta_min, theta_max, points)
    theta = np.abs(signed_theta)
    phi = np.where(signed_theta >= 0.0, phi_deg, phi_deg + 180.0)
    field = array_factor(array, weights, theta, phi)
    return signed_theta, normalized_power_db(field)


def main_lobe_angle(theta_deg: np.ndarray, power_db: np.ndarray) -> float:
    return float(theta_deg[int(np.argmax(power_db))])


def beamwidth_3db(theta_deg: np.ndarray, power_db: np.ndarray) -> float | None:
    peak = int(np.argmax(power_db))
    left = peak
    while left > 0 and power_db[left] >= -3.0:
        left -= 1
    right = peak
    while right < len(power_db) - 1 and power_db[right] >= -3.0:
        right += 1
    if left == 0 or right == len(power_db) - 1:
        return None
    return float(theta_deg[right] - theta_deg[left])


def peak_sidelobe_level(
    theta_deg: np.ndarray,
    power_db: np.ndarray,
    exclude_half_width_deg: float = 8.0,
) -> float:
    peak_angle = main_lobe_angle(theta_deg, power_db)
    mask = np.abs(theta_deg - peak_angle) > exclude_half_width_deg
    if not np.any(mask):
        return float("nan")
    return float(np.max(power_db[mask]))


def save_cut_csv(path: str | Path, theta_deg: np.ndarray, power_db: np.ndarray) -> None:
    data = np.column_stack((theta_deg, power_db))
    np.savetxt(path, data, delimiter=",", header="theta_deg,power_db", comments="")
