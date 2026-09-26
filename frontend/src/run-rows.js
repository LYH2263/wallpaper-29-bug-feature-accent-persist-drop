// Normalize a stored run result (or live estimate response) into table rows.
export function snapshotToRows(result) {
  if (!result) return { rows: [], rollWidth: null, legacy: false }
  if (result.schema === 'feature_v1' && result.main) {
    const featureCalc = result.feature
      ? { ...result.feature, rolls: result.feature.rolls ?? 0 }
      : result.feature
    return {
      rollWidth: result.roll?.width ?? null,
      rollName: result.roll?.name ?? '',
      legacy: false,
      rows: [
        { label: '主墙', width: result.wall?.perimeter ?? null, height: result.wall?.height ?? null, calc: result.main },
        { label: '重点立面', width: result.feature_width, height: result.feature_height, calc: featureCalc },
      ],
    }
  }
  // Legacy flat snapshot (pre feature-wall): only a main line, no input geometry.
  return {
    rollWidth: null,
    rollName: '',
    legacy: true,
    rows: [{ label: '主墙', width: null, height: null, calc: result }],
  }
}

export function liveToRows(out) {
  if (!out) return { rows: [], rollWidth: null }
  return {
    rollWidth: out.roll?.width ?? null,
    rows: [
      { label: '主墙', width: out.wall?.perimeter ?? null, height: out.wall?.height ?? null,
        calc: { drops: out.drops, drop_len_m: out.drop_len_m, pattern_m: out.pattern_m,
                strips_per_roll: out.strips_per_roll, rolls: out.rolls } },
      { label: '重点立面', width: out.feature_width, height: out.feature_height, calc: out.feature },
    ],
  }
}
