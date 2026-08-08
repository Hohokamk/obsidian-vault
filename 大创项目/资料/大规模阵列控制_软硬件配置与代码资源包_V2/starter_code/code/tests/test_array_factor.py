import numpy as np

from array_factor import (
    PlanarArray,
    array_factor,
    beamwidth_3db,
    cut,
    main_lobe_angle,
    quantize_one_bit,
    steering_weights,
)


def test_single_element_constant_magnitude():
    array = PlanarArray(1, 1)
    theta = np.linspace(0, 90, 20)
    field = array_factor(array, np.ones((1, 1), complex), theta, np.zeros_like(theta))
    assert np.allclose(np.abs(field), 1.0)


def test_continuous_steering_hits_target():
    array = PlanarArray(8, 8)
    target = 20.0
    weights = steering_weights(array, target, 0.0)
    theta, db = cut(array, weights, phi_deg=0.0, points=3601)
    assert abs(main_lobe_angle(theta, db) - target) < 0.2
    assert beamwidth_3db(theta, db) is not None


def test_one_bit_weights_are_plus_minus_one():
    array = PlanarArray(4, 4)
    weights = quantize_one_bit(steering_weights(array, 25.0, 0.0))
    assert set(np.unique(weights).tolist()) <= {(-1 + 0j), (1 + 0j)}
