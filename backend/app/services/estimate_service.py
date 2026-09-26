from fastapi import HTTPException

from app.engines.wallpaper_math import roll_count
from app.modules import feature_wall
from app.repositories import history, rolls, walls


def run_estimate(
    wall_id: int,
    roll_id: int,
    save: bool,
    note: str,
    feature_width: float = 0.0,
    feature_height: float = 0.0,
):
    wall = walls.get_wall(wall_id)
    if not wall:
        raise HTTPException(404, "wall not found")
    roll = rolls.get_roll(roll_id)
    if not roll:
        raise HTTPException(404, "roll not found")
    if wall.get("data_quality") == "dirty" or roll.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty seed entity")

    try:
        main_calc = roll_count(
            wall["perimeter"], wall["height"], roll["width"], roll["length"], roll["pattern_cm"]
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    feature_calc = feature_wall.build_feature(feature_width, feature_height, wall, roll)

    run_id = None
    if save:
        snapshot = feature_wall.build_run_snapshot(
            wall, roll, feature_width, feature_height, main_calc, feature_calc
        )
        run_id = history.insert_run(wall_id, roll_id, snapshot, note)
    return {
        "wall": wall,
        "roll": roll,
        "run_id": run_id,
        **main_calc,
        "feature_width": float(feature_width),
        "feature_height": float(feature_height),
        "feature": feature_calc,
    }
