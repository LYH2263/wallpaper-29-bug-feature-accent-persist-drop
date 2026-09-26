import pytest
from fastapi import HTTPException

from app import seed
from app.engines.wallpaper_math import roll_count
from app.modules import feature_wall
from app.repositories import history, rolls
from app.services.estimate_service import run_estimate


@pytest.fixture
def db_env(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "t.db")
    seed.init_db()
    return tmp_path


def test_zero_feature_matches_legacy_main(db_env):
    out = run_estimate(1, 1, False, "", 0.0, 0.0)
    base = roll_count(16.0, 2.7, 0.53, 10.0, 0)
    for k, v in base.items():
        assert out[k] == v
    assert out["feature"] == {
        "drops": 0, "drop_len_m": 0.0, "pattern_m": 0.0,
        "strips_per_roll": 0, "rolls": 0,
    }
    assert out["run_id"] is None
    assert history.list_runs(100) == []


def test_feature_height_over_wall_422_and_no_row(db_env):
    with pytest.raises(HTTPException) as ei:
        run_estimate(1, 1, True, "", 1.0, 3.0)
    assert ei.value.status_code == 422
    assert history.list_runs(100) == []


def test_negative_and_degenerate_422(db_env):
    with pytest.raises(HTTPException) as ei:
        run_estimate(1, 1, True, "", -1.0, 2.4)
    assert ei.value.status_code == 422
    with pytest.raises(HTTPException) as ei:
        run_estimate(1, 1, True, "", 3.0, 0.0)
    assert ei.value.status_code == 422
    assert history.list_runs(100) == []


def test_save_pins_one_snapshot_row(db_env):
    out = run_estimate(1, 1, True, "电视墙", 3.2, 2.4)
    assert out["run_id"] == 1
    rows = history.list_runs(100)
    assert len(rows) == 1
    snap = rows[0]["result"]
    assert snap["schema"] == "feature_v1"
    assert snap["wall"]["perimeter"] == 16.0
    assert snap["wall"]["height"] == 2.7
    assert snap["roll"]["width"] == 0.53
    assert snap["feature_width"] == 3.2
    assert snap["feature_height"] == 2.4
    assert snap["main"] == {
        "drops": 31, "drop_len_m": 2.7, "pattern_m": 0.0,
        "strips_per_roll": 3, "rolls": 11,
    }
    assert snap["feature"] == {
        "drops": 7, "drop_len_m": 2.4, "pattern_m": 0.0,
        "strips_per_roll": 4, "rolls": 2,
    }


def test_width_change_does_not_recompute_history(db_env):
    run_estimate(1, 1, True, "", 3.2, 2.4)
    updated = rolls.update_width(1, 0.7)
    assert updated["width"] == 0.7

    saved = history.list_runs(100)[0]["result"]
    assert saved["roll"]["width"] == 0.53
    assert saved["main"]["rolls"] == 11
    assert saved["feature"]["rolls"] == 2

    fresh = run_estimate(1, 1, False, "", 0.0, 0.0)
    assert fresh["drops"] == 23  # ceil(16 / 0.7)


def test_list_runs_wall_filter(db_env):
    run_estimate(1, 1, True, "", 3.2, 2.4)
    run_estimate(2, 1, True, "", 0.0, 0.0)
    assert len(history.list_runs(100)) == 2
    wall1 = history.list_runs(100, wall_id=1)
    assert len(wall1) == 1
    assert wall1[0]["wall_id"] == 1


def test_legacy_merged_row_is_split_back_on_read(db_env):
    # Snapshot shape written by the old merge-on-persist build.
    corrupted = {
        "schema": "feature_v1",
        "wall_id": 1,
        "roll_id": 1,
        "wall": {"id": 1, "name": "主卧一圈", "perimeter": 16.0, "height": 2.7},
        "roll": {"id": 1, "name": "素色53", "width": 0.53, "length": 10.0, "pattern_cm": 0},
        "feature_width": 3.2,
        "feature_height": 2.4,
        "main": {"drops": 31, "drop_len_m": 2.7, "pattern_m": 0.0,
                 "strips_per_roll": 3, "rolls": 13},
        "feature": {"drops": 0, "drop_len_m": 2.4, "pattern_m": 0.0,
                    "strips_per_roll": 4, "rolls": 0},
        "list_main_rolls": 11,
        "list_feature_rolls": 2,
    }
    history.insert_run(1, 1, corrupted, "")

    snap = history.list_runs(100)[0]["result"]
    assert snap["main"]["rolls"] == 11
    assert snap["feature"]["rolls"] == 2
    assert snap["feature"]["drops"] == 7
    assert "list_main_rolls" not in snap
    assert "list_feature_rolls" not in snap

    # Repair is read-only and idempotent across repeated opens.
    again = history.list_runs(100)[0]["result"]
    assert again["main"]["rolls"] == 11
    assert again["feature"] == snap["feature"]


def test_zero_width_save_round_trips_as_full_wall_main(db_env):
    run_estimate(1, 1, True, "", 0.0, 0.0)
    snap = history.list_runs(100)[0]["result"]
    assert snap["schema"] == "feature_v1"
    assert snap["feature"] == {
        "drops": 0, "drop_len_m": 0.0, "pattern_m": 0.0,
        "strips_per_roll": 0, "rolls": 0,
    }
    assert snap["main"] == roll_count(16.0, 2.7, 0.53, 10.0, 0)


def test_module_validation_without_db():
    wall = {"height": 2.7}
    roll = {"width": 0.53, "length": 10.0, "pattern_cm": 0}
    with pytest.raises(HTTPException) as ei:
        feature_wall.validate_feature_geometry(1.0, 2.8, wall["height"])
    assert ei.value.status_code == 422
    feature_wall.validate_feature_geometry(1.0, 2.7, wall["height"])  # equal is allowed
    calc = feature_wall.build_feature(3.2, 2.4, {"height": 2.7}, roll)
    assert calc == {
        "drops": 7, "drop_len_m": 2.4, "pattern_m": 0.0,
        "strips_per_roll": 4, "rolls": 2,
    }
