"""Repair feature-wall snapshots saved by the old merge-on-persist version.

New writes already keep the two tracks separate under ``main`` and ``feature``.
Rows written by older builds had feature rolls folded into ``main.rolls`` and
the feature block zeroed, with the real split stashed in side keys. This
module restores those rows on read without mutating the stored JSON.
"""

from __future__ import annotations

from copy import deepcopy

from app.engines.helpers import ceil_units


def restore_saved_split(result: dict) -> dict:
    """Return a view of a saved snapshot with per-track rolls intact.

    - Non feature_v1 snapshots and already-correct rows pass through.
    - Legacy merged rows (side keys present) get ``main.rolls`` and
      ``feature.rolls`` restored; ``feature.drops`` is recomputed from the
      pinned feature width and roll width. The side keys are removed.
    """
    if not isinstance(result, dict):
        return result
    out = deepcopy(result)
    if out.get("schema") != "feature_v1":
        return out
    if "list_main_rolls" not in out and "list_feature_rolls" not in out:
        return out

    main = dict(out.get("main") or {})
    feature = dict(out.get("feature") or {})
    if "list_main_rolls" in out:
        main["rolls"] = int(out["list_main_rolls"] or 0)
    if "list_feature_rolls" in out:
        feature["rolls"] = int(out["list_feature_rolls"] or 0)

    fw = float(out.get("feature_width") or 0)
    roll_width = float((out.get("roll") or {}).get("width") or 0)
    feature["drops"] = ceil_units(fw / roll_width) if fw > 0 and roll_width > 0 else 0

    out["main"] = main
    out["feature"] = feature
    out.pop("list_feature_rolls", None)
    out.pop("list_main_rolls", None)
    return out
