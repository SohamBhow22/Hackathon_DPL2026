# Aggregation Validation Contract

## 1. Purpose

Define the validation requirements for analytical datasets
created from the DPL 2026 delivery-level dataset.

## 2. Source Dataset

Expected source dataset:
- Rows: 34,967
- Columns: 61
- Distinct matches: 145
- Seasons: 2023 and 2024

The source dataset must remain immutable.

## 3. Grain and Key Uniqueness

Every aggregated dataset must have a declared grain.

Required uniqueness checks:

- Match innings: (p_match, inns)
- Team-match: (p_match, team)
- Team-season: (team, year)
- Player-season batting: (p_bat, year)
- Player-season bowling: (p_bowl, year)
- Player-season-phase batting:
  (p_bat, year, match_phase)
- Player-season-phase bowling:
  (p_bowl, year, match_phase)

Any duplicate aggregation keys must be investigated.

## 4. Batting Reconciliation

For each batter-season group:

- Aggregated runs must equal the sum of batruns.
- Aggregated balls faced must equal the sum of ballfaced.
- Aggregated batting dot-ball candidates must equal
  the sum of batting_dot.

Strike rate must be recalculated from aggregated runs
and balls faced. Do not average delivery-level strike rates.

## 5. Bowling Reconciliation

For each bowler-season group:

- Aggregated runs conceded must equal the sum of bowlruns.
- Aggregated legal balls must equal the sum of legal_delivery.
- Aggregated dot balls must equal the sum of bowling_dot.
- Aggregated candidate bowler-credited wickets must equal
  the sum of bowler_credited_wicket.

Economy rate must be recalculated from aggregated runs
and legal balls. Do not average delivery-level economy rates.

Known bowlruns anomalies must remain documented.

## 6. Team and Match Reconciliation

- Innings scores must reconcile to the sum of delivery score.
- Match results must be deduplicated before team-season aggregation.
- Match counts must count distinct represented matches.
- Unclassified results must not be treated as losses.
- Match completeness must be investigated where only one
  batting team is represented.

## 7. Phase Reconciliation

Where the definitions permit:

- Sum phase-specific batting runs to overall batting runs.
- Sum phase-specific balls faced to overall balls faced.
- Sum phase-specific bowling runs to overall bowling runs.
- Sum phase-specific legal balls to overall legal balls.
- Sum phase-specific dots and candidate wickets to their
  overall totals.

Rows with missing or invalid phases must be reported separately.

## 8. Rate Calculations

Rates must be calculated from their aggregate numerators
and denominators.

- Strike rate = runs / balls faced * 100
- Economy = runs conceded / legal balls * 6
- Batting dot-ball percentage =
  batting dot-ball candidates / balls faced * 100
- Bowling dot-ball percentage =
  bowling dot balls / legal balls * 100
- Wickets per 100 legal balls =
  candidate bowler-credited wickets / legal balls * 100

A zero denominator produces an undefined rate, not zero.

## 9. Acceptance Criteria

An analytical dataset may be accepted when:

1. Its grouping keys are unique.
2. Required identifiers are not silently discarded.
3. Aggregated counts and totals reconcile to source records.
4. Rates use the correct aggregate denominators.
5. Known source-data anomalies remain documented.
6. Excluded or unclassified records are accounted for.
7. The raw dataset remains unchanged.

Any failed validation must be investigated before the dataset
is used for player rankings or strategic recommendations.

## 10. Player-Level Aggregation Validation

### Structural and Grain Validation

The following datasets passed structural and grain validation:

| Dataset | Rows | Duplicate Keys | Missing Player IDs |
|---|---:|---:|---:|
| Player-season batting | 347 | 0 | 0 |
| Player-season bowling | 273 | 0 | 0 |
| Player-season-phase batting | 733 | 0 | 0 |
| Player-season-phase bowling | 672 | 0 | 0 |

Both seasons, 2023 and 2024, are represented in every dataset.
All phase-level records use the expected Powerplay, Middle, or Death
classification.

### Player Identity Validation

- Batter IDs associated with multiple names: 0
- Bowler IDs associated with multiple names: 0

### Phase-to-Season Reconciliation

Batting: all 347 player-season records matched. Runs, balls faced,
dot balls, boundary balls, and boundary runs reconciled with zero
mismatches.

Bowling: all 273 player-season records matched. Runs conceded,
legal balls, dot balls, and wickets reconciled with zero mismatches.

### Limitations

Successful reconciliation establishes consistency between aggregation
levels, not the independent correctness of every source metric.
Previously identified bowling-run anomalies remain unresolved and
must be considered when interpreting bowling performance.