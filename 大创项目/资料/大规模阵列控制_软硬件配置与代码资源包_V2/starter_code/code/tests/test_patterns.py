from pathlib import Path

import numpy as np

from patterns import checkerboard, load_config, one, pack_pattern, random_pattern, unpack_pattern

CONFIG = Path(__file__).resolve().parents[1] / "config" / "array_config.yaml"


def test_config_and_byte_count():
    config = load_config(CONFIG)
    assert config.channels == 256
    assert config.byte_count == 32


def test_pack_unpack_single_point():
    config = load_config(CONFIG)
    pattern = one(config, 0, 0)
    packed = pack_pattern(pattern, config)
    assert len(packed) == 32
    assert packed[0] == 0x01
    restored = unpack_pattern(packed, config)
    assert np.array_equal(restored, pattern)


def test_pack_unpack_checkerboard():
    config = load_config(CONFIG)
    pattern = checkerboard(config)
    assert np.array_equal(unpack_pattern(pack_pattern(pattern, config), config), pattern)


def test_random_reproducible():
    config = load_config(CONFIG)
    assert np.array_equal(random_pattern(config, 2026), random_pattern(config, 2026))
