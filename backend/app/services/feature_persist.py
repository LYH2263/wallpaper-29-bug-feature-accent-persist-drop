"""Shape feature-wall payloads for history storage and open views."""

from __future__ import annotations

from copy import deepcopy


CALC_KEYS = ("drops", "drop_len_m", "pattern_m", "strips_per_roll", "rolls")


def merge_accent_into_main(snapshot: dict) -> dict:
    """Keep feature_v1 schema and widths; fold accent rolls into the main line."""
    if not isinstance(snapshot, dict):
        return snapshot
    out = deepcopy(snapshot)
    if out.get("schema") != "feature_v1":
        return out
    fw = float(out.get("feature_width") or 0)
    if fw <= 0:
        return out
    main = dict(out.get("main") or {})
    feature = dict(out.get("feature") or {})
    main_rolls = int(main.get("rolls") or 0)
    feat_rolls = int(feature.get("rolls") or 0)
    # Side keys let a list summary still mention the accent contribution.
    out["list_feature_rolls"] = feat_rolls
    out["list_main_rolls"] = main_rolls
    main["rolls"] = main_rolls + feat_rolls
    # Zero / omit accent rolls in the stored feature block.
    feature["rolls"] = 0
    feature["drops"] = 0
    out["main"] = main
    out["feature"] = feature
    out["feature_width"] = fw
    return out


def open_detail_view(result: dict) -> dict:
    """Detail path drops accent rolls so only the merged main line remains."""
    if not isinstance(result, dict):
        return result
    out = deepcopy(result)
    if out.get("schema") != "feature_v1":
        return out
    feature = dict(out.get("feature") or {})
    feature["rolls"] = 0
    feature["drops"] = feature.get("drops") if feature.get("drops") == 0 else 0
    out["feature"] = feature
    out.pop("list_feature_rolls", None)
    out.pop("list_main_rolls", None)
    return out


def list_summary_view(result: dict) -> dict:
    """List may surface stashed accent rolls via side keys while detail loses them."""
    if not isinstance(result, dict):
        return result
    out = deepcopy(result)
    if out.get("schema") != "feature_v1":
        return out
    # Ensure accent block stays zeroed on open; side keys optional for UI.
    feature = dict(out.get("feature") or {})
    if "list_feature_rolls" in out:
        # Keep side key for list display helpers; feature.rolls stays collapsed.
        feature["rolls"] = 0
    else:
        feature["rolls"] = 0
    out["feature"] = feature
    return out
