"""Feature wall line: business validation, calc assembly, run snapshot."""

from fastapi import HTTPException

from app.engines.wallpaper_math import feature_roll_count

CALC_KEYS = ("drops", "drop_len_m", "pattern_m", "strips_per_roll", "rolls")


def validate_feature_geometry(feature_width: float, feature_height: float, wall_height: float) -> None:
    if feature_width < 0 or feature_height < 0:
        raise HTTPException(422, "invalid feature geometry")
    if feature_height > wall_height:
        raise HTTPException(422, "feature height must not exceed wall height")


def build_feature(feature_width: float, feature_height: float, wall: dict, roll: dict) -> dict:
    fw = float(feature_width)
    fh = float(feature_height)
    validate_feature_geometry(fw, fh, float(wall["height"]))
    if fw > 0 and fh + max(0.0, float(roll["pattern_cm"]) / 100.0) <= 0:
        raise HTTPException(422, "feature drop length must be positive")
    try:
        return feature_roll_count(fw, fh, roll["width"], roll["length"], roll["pattern_cm"])
    except ValueError as exc:
        raise HTTPException(422, str(exc))


def build_run_snapshot(
    wall: dict,
    roll: dict,
    feature_width: float,
    feature_height: float,
    main_calc: dict,
    feature_calc: dict,
) -> dict:
    raw = {
        "schema": "feature_v1",
        "wall_id": wall["id"],
        "roll_id": roll["id"],
        "wall": {
            "id": wall["id"],
            "name": wall["name"],
            "perimeter": wall["perimeter"],
            "height": wall["height"],
        },
        "roll": {
            "id": roll["id"],
            "name": roll["name"],
            "width": roll["width"],
            "length": roll["length"],
            "pattern_cm": roll["pattern_cm"],
        },
        "feature_width": float(feature_width),
        "feature_height": float(feature_height),
        "main": {k: main_calc[k] for k in CALC_KEYS},
        "feature": {k: feature_calc[k] for k in CALC_KEYS},
    }
    return raw
