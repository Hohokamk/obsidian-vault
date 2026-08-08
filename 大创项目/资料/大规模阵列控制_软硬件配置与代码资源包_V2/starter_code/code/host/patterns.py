"""Pattern generation and logical-to-physical packing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np
import yaml


@dataclass(frozen=True, slots=True)
class ArrayConfig:
    rows: int
    cols: int
    channels: int
    mapping: np.ndarray
    bit_order: str = "lsb_first"
    active_high: bool = True

    @property
    def byte_count(self) -> int:
        return (self.channels + 7) // 8


def load_config(path: str | Path) -> ArrayConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    arr = raw["array"]
    ser = raw.get("serialization", {})
    rows, cols, channels = int(arr["rows"]), int(arr["cols"]), int(arr["channels"])
    if rows * cols != channels:
        raise ValueError("rows*cols must equal channels for the baseline rectangular array")

    mapping_spec = raw.get("mapping", {"type": "identity"})
    if mapping_spec.get("type") == "identity":
        mapping = np.arange(channels, dtype=np.int32)
    elif mapping_spec.get("type") == "explicit":
        mapping = np.asarray(mapping_spec["logical_to_physical"], dtype=np.int32)
    else:
        raise ValueError(f"unsupported mapping type: {mapping_spec.get('type')}")
    if mapping.shape != (channels,):
        raise ValueError("mapping length mismatch")
    if sorted(mapping.tolist()) != list(range(channels)):
        raise ValueError("mapping must be a permutation of all physical channels")

    return ArrayConfig(
        rows=rows,
        cols=cols,
        channels=channels,
        mapping=mapping,
        bit_order=ser.get("bit_order_within_byte", "lsb_first"),
        active_high=bool(ser.get("active_high_logical", True)),
    )


def empty(config: ArrayConfig) -> np.ndarray:
    return np.zeros((config.rows, config.cols), dtype=np.uint8)


def full(config: ArrayConfig) -> np.ndarray:
    return np.ones((config.rows, config.cols), dtype=np.uint8)


def one(config: ArrayConfig, row: int, col: int) -> np.ndarray:
    if not (0 <= row < config.rows and 0 <= col < config.cols):
        raise ValueError("row/col out of range")
    result = empty(config)
    result[row, col] = 1
    return result


def checkerboard(config: ArrayConfig, invert: bool = False) -> np.ndarray:
    r, c = np.indices((config.rows, config.cols))
    result = ((r + c) & 1).astype(np.uint8)
    return 1 - result if invert else result


def border(config: ArrayConfig) -> np.ndarray:
    result = empty(config)
    result[0, :] = 1
    result[-1, :] = 1
    result[:, 0] = 1
    result[:, -1] = 1
    return result


def random_pattern(config: ArrayConfig, seed: int, density: float = 0.5) -> np.ndarray:
    if not 0.0 <= density <= 1.0:
        raise ValueError("density must be between 0 and 1")
    rng = np.random.default_rng(seed)
    return (rng.random((config.rows, config.cols)) < density).astype(np.uint8)


def pack_pattern(pattern: np.ndarray, config: ArrayConfig) -> bytes:
    pattern = np.asarray(pattern, dtype=np.uint8)
    if pattern.shape != (config.rows, config.cols):
        raise ValueError(f"expected shape {(config.rows, config.cols)}, got {pattern.shape}")
    if np.any((pattern != 0) & (pattern != 1)):
        raise ValueError("pattern must contain only 0/1")

    logical = pattern.reshape(-1)
    physical = np.zeros(config.channels, dtype=np.uint8)
    physical[config.mapping] = logical
    if not config.active_high:
        physical = 1 - physical

    packed = bytearray(config.byte_count)
    for physical_index, value in enumerate(physical):
        if not value:
            continue
        byte_index = physical_index // 8
        bit_index = physical_index % 8
        if config.bit_order == "msb_first":
            bit_index = 7 - bit_index
        elif config.bit_order != "lsb_first":
            raise ValueError(f"unsupported bit order: {config.bit_order}")
        packed[byte_index] |= 1 << bit_index
    return bytes(packed)


def unpack_pattern(payload: bytes, config: ArrayConfig) -> np.ndarray:
    if len(payload) != config.byte_count:
        raise ValueError("payload length mismatch")
    physical = np.zeros(config.channels, dtype=np.uint8)
    for physical_index in range(config.channels):
        byte_index = physical_index // 8
        bit_index = physical_index % 8
        if config.bit_order == "msb_first":
            bit_index = 7 - bit_index
        physical[physical_index] = (payload[byte_index] >> bit_index) & 1
    if not config.active_high:
        physical = 1 - physical
    logical = np.zeros(config.channels, dtype=np.uint8)
    logical[:] = physical[config.mapping]
    return logical.reshape(config.rows, config.cols)


def save_pattern(path: str | Path, pattern: np.ndarray) -> None:
    path = Path(path)
    if path.suffix.lower() == ".npy":
        np.save(path, np.asarray(pattern, dtype=np.uint8))
    elif path.suffix.lower() == ".csv":
        np.savetxt(path, np.asarray(pattern, dtype=np.uint8), fmt="%d", delimiter=",")
    else:
        raise ValueError("supported output formats: .npy, .csv")


def load_pattern(path: str | Path) -> np.ndarray:
    path = Path(path)
    if path.suffix.lower() == ".npy":
        return np.load(path)
    if path.suffix.lower() == ".csv":
        return np.loadtxt(path, delimiter=",", dtype=np.uint8)
    raise ValueError("supported input formats: .npy, .csv")
