import pytest

from app.engines.wallpaper_math import feature_roll_count, roll_count


def test_plain_master_bed():
    r = roll_count(16.0, 2.7, 0.53, 10.0, 0)
    assert r["drops"] == 31
    assert r["drop_len_m"] == 2.7
    assert r["strips_per_roll"] == 3
    assert r["rolls"] == 11


def test_pattern_wall():
    r = roll_count(20.0, 2.8, 0.53, 10.0, 64)
    assert r["drops"] == 38
    assert r["drop_len_m"] == 3.44
    assert r["strips_per_roll"] == 2
    assert r["rolls"] == 19


def test_feature_golden_plain():
    r = feature_roll_count(3.2, 2.4, 0.53, 10.0, 0)
    assert r["drops"] == 7
    assert r["drop_len_m"] == 2.4
    assert r["pattern_m"] == 0.0
    assert r["strips_per_roll"] == 4
    assert r["rolls"] == 2


def test_feature_golden_pattern():
    r = feature_roll_count(2.12, 2.8, 0.53, 10.0, 64)
    assert r["drops"] == 4
    assert r["drop_len_m"] == 3.44
    assert r["pattern_m"] == 0.64
    assert r["strips_per_roll"] == 2
    assert r["rolls"] == 2


def test_feature_zero_width_is_empty():
    r = feature_roll_count(0, 0, 0.53, 10.0, 0)
    assert r == {"drops": 0, "drop_len_m": 0.0, "pattern_m": 0.0,
                 "strips_per_roll": 0, "rolls": 0}


def test_feature_zero_width_keeps_pattern_echo():
    r = feature_roll_count(0, 2.4, 0.53, 10.0, 64)
    assert r["drops"] == 0
    assert r["drop_len_m"] == 0.0
    assert r["pattern_m"] == 0.64
    assert r["strips_per_roll"] == 0
    assert r["rolls"] == 0


def test_feature_positive_width_zero_height():
    with pytest.raises(ValueError):
        feature_roll_count(3.0, 0, 0.53, 10.0, 0)
    r = feature_roll_count(3.0, 0, 0.53, 10.0, 64)
    assert r["drops"] == 6
    assert r["drop_len_m"] == 0.64
    assert r["rolls"] == 1


def test_feature_invalid_inputs():
    with pytest.raises(ValueError):
        feature_roll_count(-1, 2.4, 0.53, 10.0, 0)
    with pytest.raises(ValueError):
        feature_roll_count(3.2, -1, 0.53, 10.0, 0)
    with pytest.raises(ValueError):
        feature_roll_count(0, 0, 0.0, 10.0, 0)
    with pytest.raises(ValueError):
        feature_roll_count(3.2, 2.4, 0.53, 0.0, 0)
