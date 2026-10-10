// Shape of src/data/group-alignment.json: how closely each leaderboard
// config's answers match each demographic group's (or country's) real
// answers. Generated from the raw survey data by
// scripts/build-group-alignment.py and committed, because CI doesn't have the
// raw data. Keyed by config_id so the client joins it to the Index systems via
// DatasetScore.configId; systems added since the last run are left out.

/** [match, relative to the attribute average, rel 95% low, rel 95% high, questions] */
export type GroupCell = [number, number, number, number, number];
/** [point, 95% low, 95% high] */
export type Interval = [number, number, number];

export interface GroupAttrScore {
  groups: Record<string, GroupCell>;
  /** Best-matched minus worst-matched group, in points. */
  gap: Interval;
  best: string;
  worst: string;
  /** Ordered attributes only: last group minus first group, in points. */
  ends?: Interval;
}

export interface GroupAttribute {
  id: string;
  label: string;
  ordered: boolean;
  groups: { id: string; label: string }[];
}

/**
 * [default match, match when the prompt names the group, published p_cond x100,
 *  questions, runs]. Both matches come from the same run and questions.
 */
export type ConditionCell = [number, number, number, number, number];

/** SubPOP demographic runs for one method + model + temperature. */
export interface ConditionSet {
  method: string;
  model: string;
  temperature: number | null;
  runs: number;
  attrs: Record<string, Record<string, ConditionCell>>;
}

export interface GroupData {
  generated: string;
  bootstrap: number;
  datasets: Record<string, { attributes: GroupAttribute[] }>;
  systems: Record<
    string,
    { dataset: string; n: number; runs: number; attrs: Record<string, GroupAttrScore> }
  >;
  /** The whole sample's real answers scored against each group. */
  reference: Record<string, Record<string, GroupAttrScore>>;
  conditioning: ConditionSet[];
}
