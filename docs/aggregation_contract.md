# Analytical Aggregation Contract

## 1. Purpose

Define the grains, metric formulas, aggregation rules and
comparison constraints for the DPL 2026 KKR analysis.

The contract supports reproducible team performance analysis,
player scouting and phase-specific evaluation.

## 2. Source of Truth

- Raw delivery-level data remains immutable.
- Derived features are created using reusable metric functions.
- The recorded `score` field is authoritative for delivery scores
  and team innings totals.
- The source `bowlruns` field is retained for bowling runs conceded.
- Known bowling-run anomalies must remain documented.
- Candidate bowler-credited wickets use the validated provisional
  dismissal classification.

## 3. Analytical Grains

| Dataset | Grain |
|---|---|
| Delivery features | One recorded delivery |
| Match summary | One team in one match |
| Team-season summary | One team in one season |
| Player-season batting | One batter in one season |
| Player-season bowling | One bowler in one season |
| Player-season-phase batting | One batter, season and phase |
| Player-season-phase bowling | One bowler, season and phase |

Player-match-innings detail may be retained for diagnostic analysis.

## 4. Batting Metrics

Runs:
    Sum of batruns.

Balls faced:
    Sum of ballfaced.

Strike rate:
    Runs / balls faced * 100, when balls faced > 0.

Batting dot-ball candidates:
    Sum of batting_dot.

Batting dot-ball percentage:
    Sum of batting_dot / balls faced * 100,
    when balls faced > 0.

Rates with zero denominators are undefined, not zero.

Boundary metrics remain deferred until their definitions
and source fields are validated.

## 5. Bowling Metrics

Runs conceded:
    Sum of bowlruns.

Legal balls:
    Count of legal_delivery records.

Economy rate:
    Sum of bowlruns / legal balls * 6,
    when legal balls > 0.

Dot balls:
    Sum of bowling_dot.

Bowling dot-ball percentage:
    Sum of bowling_dot / legal balls * 100,
    when legal balls > 0.

Candidate bowler-credited wickets:
    Sum of bowler_credited_wicket.

Wickets per 100 legal balls:
    Sum of bowler_credited_wicket / legal balls * 100,
    when legal balls > 0.

Known bowlruns anomalies must not be silently corrected.

## 6. Team Metrics

Team innings score:
    Sum of score within a match and innings.

Matches represented:
    Count distinct matches actually present in the data.

Win percentage:
    Wins / matches with a valid, classifiable result * 100.

Team runs and bowler-conceded runs are different measures.
Do not use the sum of bowlruns as the team's total score conceded.

## 7. Phase Analysis

Use the validated match_phase feature:

- Powerplay: overs 1-6
- Middle: overs 7-15
- Death: overs 16-20

Aggregate batting and bowling metrics separately by phase.

## 8. Comparability and Eligibility

- Retain exposure measures alongside performance rates.
- Do not exclude players based on arbitrary thresholds at this stage.
- Establish minimum sample-size requirements before final rankings.
- Analyse 2023 and 2024 separately before combining seasons.
- Compare phase-specific performance in the relevant phase.
- Treat descriptive associations as evidence, not proof of causation.

## 9. Dataset Coverage Limitations

The dataset contains 28 KKR matches across 2023 and 2024,
with 14 represented matches per season.

The 2024 Qualifier 1 and Final are included, while KKR's
last two league matches are absent.

Report coverage based on actual records. Do not imply that all
matches played by KKR in these seasons are represented.

## 10. Validation Requirements

Before analytical datasets are accepted:

- Verify their declared grain and key uniqueness.
- Reconcile aggregates against delivery-level records.
- Verify metric denominators and zero-denominator handling.
- Check that phase-level records reconcile to overall totals
  where the definitions permit reconciliation.
- Preserve and report known data-quality limitations.
- Keep the raw dataset unchanged.

## 11. Aggregation Specifications

Before implementing aggregation functions, verify:

- Actual team, season, batter, bowler and match identifier columns.
- Whether player identifiers are stable and suitable for grouping.
- Whether each match has a reliable team-level result.
- Whether the proposed grouping keys are unique at their intended grain.
- Whether all aggregate metrics reconcile to the source records.

Aggregation functions must preserve the declared grain and expose
validation failures rather than silently dropping records.

