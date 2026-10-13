# Feature Specification — KKR IPL Analytics

## 1. Purpose

This document defines the derived features required to analyse
Kolkata Knight Riders' performance in the 2023 and 2024 IPL seasons.

The objective is to identify performance strengths and weaknesses,
evaluate players within their roles, develop evidence-based scouting
profiles, and formulate practical strategic recommendations.

Features must support at least one of the following objectives:

1. Team performance evaluation.
2. Batting performance analysis.
3. Bowling performance analysis.
4. Phase-wise performance analysis.
5. Player-role evaluation.
6. Scouting and player-profile identification.
7. Match strategy analysis.

Features will be implemented only after their definitions,
calculation rules, analytical grain, and limitations are documented.

Every major analytical finding should ultimately address:

- What did we observe?
- Why might it matter?
- Which player characteristics or match situations are relevant?
- What decision could KKR consider?
- What evidence supports the recommendation?
- What limitations affect our conclusion?


## 2. Design Principles

1. Preserve the raw dataset without modification.

2. Use the analytical delivery key:
   (p_match, inns, ball_id).

3. Aggregate data only after defining the intended analytical grain.

4. Use player identifiers wherever available instead of relying
   exclusively on player names.

5. Treat score as the authoritative recorded delivery score.

6. Treat out as the authoritative wicket-event indicator.

7. Never replace missing values with zero without a justified rule.

8. Distinguish observed associations from causal explanations.

9. Avoid using information unavailable at the time a prediction
   would supposedly be made.

10. Every derived feature must have a defined analytical purpose.

11. Validate calculations against the source data and cricket rules.

12. Connect performance weaknesses to measurable player profiles
    and practical strategic decisions wherever the evidence permits.

13. Distinguish team runs from runs conceded by a bowler.

14. Use appropriate denominators when calculating rates and percentages.

15. Evaluate players in relevant roles, phases, and match situations.

16. Consider sample size and uncertainty when comparing players.

17. Distinguish conventional performance metrics from contextual
    metrics such as RAA and WAA.

18. Do not assume that a high or low value automatically indicates
    superior player quality.

19. Do not assume that a performance weakness requires recruitment.
    Investigate whether it could instead be addressed through role
    allocation or tactical changes.

20. Use only the permitted dataset unless additional sources are
    explicitly allowed and documented.


## 3. Analytical Grains

### 3.1 Delivery Grain

Key:

p_match + inns + ball_id

Purpose:

Represent individual delivery events and derive delivery-level
features such as runs, wickets, innings phases, and scoring outcomes.

Delivery-level calculations form the foundation for subsequent
player, phase, and match aggregations.

### 3.2 Player-Match-Innings Grain

Key:

Match + innings + player + role

Purpose:

Evaluate individual player contributions within specific matches,
innings, phases, and roles.

A player may have separate batting and bowling records within
the same match.

Batting and bowling metrics must be calculated using their
respective event definitions and denominators.

### 3.3 Match Grain

Key:

p_match

Purpose:

Evaluate match outcomes, team performance, innings context,
and characteristics associated with winning or losing.

Match-level calculations must avoid double-counting matches
or incorrectly treating delivery records as independent matches.

### 3.4 Phase Grain

Key:

Match + innings + team/player + phase

Purpose:

Evaluate performance during the Powerplay, middle overs,
and death overs.

Phase-level metrics must use the appropriate phase-specific
numerators and denominators.

The exact phase boundaries must be validated against the source
over-numbering convention before implementation.


## 4. Feature Categories

1. Delivery features
2. Batting features
3. Bowling features
4. Phase-level features
5. Player-profile features
6. Match-level features
7. Contextual performance metrics (RAA and WAA)


## 5. Feature Documentation Standard

Every feature must document:

- Feature name
- Analytical question
- Source columns
- Calculation rule
- Analytical grain
- Intended use
- Validation rule
- Known limitations
- Scouting or strategic relevance

Features must not be implemented solely because the required
calculation is technically possible. They must support a defined
analytical question or decision.


## 6. Delivery Features

### 6.1 Delivery Identity

Feature: Delivery key

Source columns:

- p_match
- inns
- ball_id

Calculation:

Use the composite key (p_match, inns, ball_id) to identify
a delivery record.

Purpose:

- Identify individual deliveries.
- Prevent duplicate delivery counting.
- Support reliable aggregation.

Validation:

- Check for duplicate composite keys.
- Do not assume physical CSV row order represents delivery order.

### 6.2 Delivery Scoring

Feature: Total runs

Source column:

- score

Calculation:

Use the recorded delivery score as the authoritative team
scoring value.

Purpose:

- Measure team scoring.
- Support innings and phase aggregation.

Validation:

- Do not reconstruct score by blindly summing all extras fields.
- Investigate discrepancies using the documented scoring semantics.

Feature: Batter runs

Source column:

- batruns

Calculation:

Use the recorded batter-run value.

Purpose:

- Calculate batting contribution and boundary-related metrics.

Validation:

- Confirm the relationship between batter runs, outcomes,
  and boundary indicators.

### 6.3 Wicket Events

Feature: Wicket event

Source column:

- out

Calculation:

Use out as the authoritative wicket-event indicator.

Purpose:

- Identify wicket events.
- Support batting dismissal and bowling wicket analysis.

Validation:

- Retain dismissal type and player identifiers where available.
- Do not treat bat_out as the total wicket-event indicator.
- Distinguish wickets credited to the bowler from dismissals
  that are not credited to the bowler.

### 6.4 Innings Phase

Feature: Innings phase

Source column:

- over_num

Proposed classification:

- Powerplay: overs 1-6
- Middle overs: overs 7-15
- Death overs: overs 16-20

Purpose:

- Compare performance across innings phases.
- Evaluate phase-specific player roles.
- Identify potential tactical and scouting requirements.

Validation:

- Confirm whether over_num is zero-indexed or one-indexed.
- Confirm how shortened innings are represented.
- Do not create artificial deliveries for overs that were not played.
- Document how deliveries beyond the conventional 20-over limit,
  if any, would be handled.


## 7. Batting Features

Purpose:

Understand how KKR generated runs, how batters managed scoring
opportunities and wicket risk, and which batting profiles could
address identified weaknesses.

### 7.1 Core Batting Metrics

| Feature | Source columns | Calculation or rule | Intended use |
|---|---|---|---|
| Runs scored | batruns | Sum batter runs | Measure scoring contribution |
| Balls faced | Delivery events and extras fields | Count balls faced using a validated definition | Establish batting denominators |
| Batting strike rate | Runs scored, balls faced | Runs scored / balls faced * 100 | Measure scoring speed |
| Boundary runs | batruns and validated boundary indicators | Sum batter runs from fours and sixes | Measure boundary-scoring contribution |
| Boundary Ball % | Boundary events, balls faced | Boundary balls / balls faced * 100 | Measure boundary frequency |
| Boundary Runs % | Boundary runs, total batter runs | Boundary runs / total batter runs * 100 | Measure the proportion of runs from boundaries |
| Dot-ball % | Delivery events, batter runs, extras | Validated batting dot balls / balls faced * 100 | Measure scoring stagnation |
| Non-boundary Ball % | Boundary events, balls faced | Non-boundary balls / balls faced * 100 | Supplementary description of scoring distribution |
| Dismissals | out, dismissal, p_out | Count validated dismissals attributable to the batter | Evaluate dismissal frequency |
| Runs per dismissal | Runs scored, dismissals | Runs scored / dismissals, where dismissals > 0 | Evaluate scoring output relative to dismissals |

### 7.2 Boundary Ball %

Definition:

Boundary Ball % measures the frequency with which a batter
faces a ball resulting in a four or six.

Formula:

Boundary Ball % =
Boundary-scoring balls / Balls faced * 100

A boundary-scoring ball is a delivery on which the batter is
credited with four or six runs from the bat, subject to validation
of the source's outcome and scoring fields.

Purpose:

- Identify boundary-oriented batting profiles.
- Compare boundary frequency across roles and phases.
- Investigate whether a team scoring weakness is associated
  with insufficient boundary production.

Validation:

- Confirm how boundary events are represented.
- Distinguish batter-scored boundaries from boundary extras.
- Use the validated balls-faced denominator.

### 7.3 Boundary Runs %

Definition:

Boundary Runs % measures the proportion of a batter's total
batter runs that comes from fours and sixes.

Formula:

Boundary Runs % =
Boundary runs / Total batter runs * 100

Purpose:

- Measure the contribution of boundary scoring to a batter's runs.
- Distinguish players who rely more heavily on boundary scoring
  from players who accumulate a greater proportion of runs
  through non-boundary scoring.

Validation:

- The numerator must include batter runs from fours and sixes.
- The denominator must be total batter runs, not team runs.
- A zero denominator must result in an undefined value.
- The calculation must not include byes or leg-byes as batter runs.

### 7.4 Dot-Ball %

Definition:

Dot-ball % measures the frequency of balls faced on which
the batter scores zero batter runs, subject to the validated
definition of a batting dot ball.

Formula:

Dot-ball % =
Batting dot balls / Balls faced * 100

Purpose:

- Identify scoring stagnation.
- Evaluate strike rotation and scoring pressure.
- Compare batting profiles within relevant roles and phases.

Validation:

- Distinguish batter runs from team runs.
- Do not automatically classify a wide as a conventional
  batting dot ball merely because the batter scores zero.
- Validate the treatment of byes, leg-byes, no-balls, and
  other extras.
- Use the same definition consistently across players and seasons.

### 7.5 Non-boundary Ball %

Definition:

Non-boundary Ball % measures the proportion of balls faced
that do not result in a four or six.

Formula:

Non-boundary Ball % =
Non-boundary balls / Balls faced * 100

Purpose:

Provide a supplementary description of a batter's scoring
distribution.

Important limitation:

When Boundary Ball % and Non-boundary Ball % use the same
denominator and complementary event definitions:

Boundary Ball % + Non-boundary Ball % = 100%

Therefore, Non-boundary Ball % is mathematically redundant
with Boundary Ball %.

It may be retained for descriptive reporting, but it should not
be treated as an independent performance indicator.

### 7.6 Phase-Specific Batting Metrics

Calculate the following metrics separately for the Powerplay,
middle overs, and death overs:

- Runs scored
- Balls faced
- Strike rate
- Boundary Ball %
- Boundary Runs %
- Dot-ball %
- Non-boundary Ball %, where useful
- RAA
- WAA

Purpose:

- Identify the phases in which KKR generate or lose scoring value.
- Compare player contributions within relevant phases.
- Identify measurable batting profiles that could address
  phase-specific weaknesses.

Validation:

- Use phase-specific numerators and denominators.
- Do not calculate a phase-specific rate by averaging player
  rates without considering their denominators.
- Consider sample size and match context.

### 7.7 Batting Metric Interpretation

No single metric will be treated as a complete measure of
batting quality.

Examples:

- A high Boundary Ball % indicates frequent boundary scoring,
  but does not by itself establish overall batting quality.
- A high Boundary Runs % indicates a larger proportion of runs
  comes from boundaries, but does not necessarily indicate
  greater efficiency.
- A high Dot-ball % may indicate scoring stagnation, but can
  also reflect difficult match situations or bowling quality.
- Strike rate does not independently account for wicket risk.
- Runs per dismissal must be interpreted alongside sample size
  and the player's role.

Boundary Ball % and Boundary Runs % must be calculated
independently because they measure different aspects of batting.

### 7.8 Scouting Applications

Potential batting profiles include:

Aggressive top-order batter:
- Strike rate
- Boundary Ball %
- Boundary Runs %
- Dot-ball %
- RAA
- WAA

Consistent top-order batter:
- Runs per dismissal
- RAA
- WAA
- Dot-ball %
- Sample size

Middle-over batter:
- Phase-specific strike rate
- Boundary Ball %
- Boundary Runs %
- Dot-ball %
- RAA
- WAA

Death-over batter:
- Death-over strike rate
- Boundary Ball %
- Boundary Runs %
- Dot-ball %
- RAA
- WAA

These profiles are analytical descriptions, not predetermined
rankings or fixed classifications.

Scouting recommendations must be tied to performance gaps
identified in the data.


## 8. Bowling Features

Purpose:

Understand how effectively KKR restricted scoring, created
dismissal opportunities, and performed across innings phases.

### 8.1 Core Bowling Metrics

| Feature | Source columns | Calculation or rule | Intended use |
|---|---|---|---|
| Runs conceded | score and extras-related fields | Calculate runs charged to the bowler under applicable cricket rules | Measure run prevention |
| Legal balls bowled | Delivery events and extras fields | Count legal deliveries under applicable rules | Establish bowling denominators |
| Bowling economy | Runs conceded, legal balls | Runs conceded / legal balls * 6 | Measure overall run containment |
| Dot-ball % | Delivery events, score, extras | Legal deliveries on which the batting team scores zero / legal deliveries * 100 | Measure scoring suppression |
| Non-dot economy rate | Bowler-conceded runs on non-dot legal deliveries, non-dot legal deliveries | Bowler-conceded runs on non-dot legal deliveries / non-dot legal deliveries * 6 | Measure the cost of scoring opportunities |
| Bowler-credited wickets | out, dismissal, p_out | Count wickets credited to the bowler under applicable rules | Measure wicket-taking |
| Wickets per 100 legal balls | Bowler-credited wickets, legal balls | Bowler-credited wickets / legal balls * 100 | Compare wicket-taking frequency |
| Boundary concession rate | Validated boundary events, legal deliveries | Define numerator and denominator explicitly | Evaluate boundary prevention |
| Bowling workload | Legal balls bowled | Aggregate by player and match | Understand usage and workload |

### 8.2 Bowling Economy

Definition:

Bowling economy measures the number of runs conceded by a bowler
per six legal deliveries.

Formula:

Bowling Economy =
Bowler-conceded runs / Legal balls bowled * 6

Purpose:

- Measure run containment.
- Compare bowlers within relevant roles and phases.
- Establish a conventional baseline for contextual metrics.

Validation:

- Distinguish team runs from bowler-conceded runs.
- Handle byes, leg-byes, wides, and no-balls according to
  applicable scoring rules.
- Use legal deliveries as the denominator.
- Handle zero legal deliveries explicitly.

### 8.3 Bowling Dot-Ball %

Definition:

Bowling Dot-ball % measures the proportion of legal deliveries
on which the batting team scores zero total runs.

Formula:

Bowling Dot-ball % =
Team-scoring dot deliveries / Legal deliveries * 100

Purpose:

- Evaluate scoring suppression.
- Identify bowlers who frequently prevent scoring.
- Compare performance across innings phases.

Validation:

- Use legal deliveries as the denominator.
- Count team runs, not just batter runs, when determining
  whether the team scored on a delivery.
- Validate the handling of byes, leg-byes, wides, and no-balls.
- A legal delivery on which the team scores only byes or
  leg-byes is not a team-scoring dot ball.

### 8.4 Non-Dot Economy Rate

Definition:

Non-dot economy rate measures bowler-conceded runs on
non-dot legal deliveries relative to the number of such deliveries.

Formula:

Non-dot Economy Rate =
Bowler-conceded runs on non-dot legal deliveries /
Non-dot legal deliveries * 6

A non-dot legal delivery is a legal delivery on which the
batting team scores at least one run.

Purpose:

- Evaluate the cost of scoring opportunities.
- Distinguish scoring suppression from the cost of scoring
  when the batting team does score.
- Develop more detailed bowling profiles.

Validation:

- Use non-dot legal deliveries in the denominator.
- Use the corresponding bowler-conceded runs in the numerator.
- Do not automatically include all team runs in the numerator.
- Define the treatment of byes and leg-byes consistently.
- Handle wides and no-balls separately according to the chosen
  definition.
- Return an undefined value when the denominator is zero.

Interpretation:

Non-dot economy rate must be evaluated alongside overall
economy and Dot-ball %.

A bowler may have a low non-dot economy rate but still concede
too many runs overall if the bowler produces too few dot balls.

### 8.5 Wickets per 100 Legal Balls

Formula:

Wickets per 100 Legal Balls =
Bowler-credited wickets / Legal balls bowled * 100

Purpose:

- Compare wicket-taking frequency.
- Complement economy and Dot-ball %.
- Evaluate phase-specific wicket-taking.

Validation:

- Count only wickets credited to the bowler.
- Do not count all out=True events as bowler-credited wickets.
- Use legal balls as the denominator.
- Handle zero legal deliveries explicitly.

### 8.6 Phase-Specific Bowling Metrics

Calculate the following separately for the Powerplay,
middle overs, and death overs:

- Runs conceded
- Legal balls bowled
- Economy rate
- Dot-ball %
- Non-dot economy rate
- Bowler-credited wickets
- Wickets per 100 legal balls
- Boundary concession rate
- RAA
- WAA

Purpose:

- Identify phase-specific bowling strengths and weaknesses.
- Evaluate bowlers within comparable roles.
- Identify bowling profiles that could address observed weaknesses.

Validation:

- Use phase-specific numerators and denominators.
- Apply the same definitions across seasons.
- Consider differences in match context and sample size.

### 8.7 Bowling Metric Interpretation

No single metric will be treated as a complete measure of
bowling quality.

Examples:

- A low economy rate indicates better run containment, but
  does not independently measure wicket-taking.
- A high Dot-ball % indicates frequent scoring suppression,
  but does not establish that the bowler is effective in
  every match situation.
- A low non-dot economy rate indicates lower bowler-conceded
  runs on the selected subset of deliveries, but does not
  measure how often scoring opportunities occur.
- A high wicket-taking rate must be interpreted in the context
  of dismissal type, workload, phase, and sample size.

Dot-ball % and non-dot economy rate must be interpreted together.

### 8.8 Scouting Applications

Potential bowling profiles include:

Powerplay bowler:
- Economy
- Dot-ball %
- WAA
- RAA

Middle-over bowler:
- Economy
- Dot-ball %
- Non-dot economy rate
- RAA
- WAA

Death-over bowler:
- Economy
- Dot-ball %
- Non-dot economy rate
- RAA
- WAA

These profiles are intended to identify measurable performance
characteristics, not to establish a player's underlying technical
ability or guarantee future performance.


## 9. Phase-Level Features

Purpose:

Evaluate how KKR performed during different stages of an innings.

Phases:

- Powerplay: overs 1-6
- Middle overs: overs 7-15
- Death overs: overs 16-20

The phase boundaries must be validated against the source's
over-numbering convention before implementation.

### 9.1 Team Batting Features by Phase

- Runs scored
- Balls faced
- Scoring rate
- Wickets lost
- Boundary Ball %
- Boundary Runs %
- Dot-ball %
- RAA
- WAA

### 9.2 Team Bowling Features by Phase

- Runs conceded
- Legal balls
- Economy rate
- Dot-ball %
- Non-dot economy rate
- Wickets taken
- Wickets per 100 legal balls
- RAA
- WAA

### 9.3 Interpretation

Phase-level comparisons should use rates and appropriate
denominators rather than raw totals alone.

Shortened innings and matches with fewer deliveries must be
handled explicitly.

The analysis should investigate whether phase-level weaknesses
are associated with particular players, roles, or match situations.

A phase-level weakness does not automatically imply a recruitment
need. Role allocation and tactical changes must also be considered.


## 10. Player-Profile and Scouting Requirements

Player comparisons must account for:

1. Relevant player roles.
2. Innings phase.
3. Match situation.
4. Sample size.
5. Season-specific performance.
6. Scoring efficiency.
7. Wicket risk or wicket-taking.
8. Contextual performance relative to expectations.

Raw totals must not be treated as sufficient evidence of
player quality.

Player profiles must be derived from measurable characteristics.

Recruitment needs must be distinguished from tactical or
role-allocation issues.

Recommendations must be supported by observed evidence.

The analysis must explicitly identify scouting questions that
the supplied dataset cannot answer.

### 10.1 Scouting Decision Framework

For each major performance weakness:

1. Identify the observed performance gap.
2. Determine when and under what conditions it occurs.
3. Investigate which existing players and roles are associated
   with the gap.
4. Identify measurable player characteristics that could address it.
5. Evaluate whether the issue may be related to player capability,
   role allocation, or match strategy.
6. Define the player profile or tactical adjustment that could
   address the gap.
7. State the evidence supporting the recommendation.
8. Document uncertainty and limitations.

### 10.2 Example

Observed gap:

KKR appear to concede too many runs during the death overs.

Diagnostic questions:

- Is the problem excessive boundary scoring, insufficient
  wicket-taking, or both?
- Is the weakness concentrated among particular bowlers?
- Does it persist across both seasons?
- Does it vary with match situation?

Potential player-profile implication:

Identify measurable bowling characteristics associated with
better death-over performance.

Potential strategic implication:

Evaluate whether existing bowlers could be deployed differently
or whether a different bowling profile may be required.

Important limitation:

The analysis may identify desirable player characteristics,
but it cannot establish that a particular real-world recruit
would improve KKR without additional evidence.


## 11. Match-Level Features

Purpose:

Understand team-level characteristics associated with match outcomes.

### 11.1 Match Result

Source columns:

- p_match
- winner
- team_bat
- team_bowl

Features:

- Match identifier
- Match result
- Winning team
- Innings count
- Match completeness
- KKR batting-first or chasing context

Validation:

- Ensure one consistent match-level record per match.
- Identify incomplete matches.
- Do not treat an unresolved or incomplete result as an ordinary loss.

### 11.2 Innings Features

Features:

- First-innings total
- Second-innings total
- Wickets lost by innings
- Phase-specific performance
- Batting and bowling contributions

Validation:

- Respect the natural innings order.
- Do not rely on physical CSV row order.
- Use the validated delivery ordering.

### 11.3 Match Strategy Analysis

Potential questions:

- How did KKR perform when batting first versus chasing?
- Which phase-level patterns were associated with wins and losses?
- Were particular player roles more valuable in specific situations?
- Which tactical adjustments are supported by recurring evidence?

### 11.4 Leakage Prevention

Match-result information must not be used to construct a feature
that is presented as available before the match or before the
relevant prediction point.

The timing of each feature must be documented when predictive
analysis is undertaken.

Match-level observations should not automatically be interpreted
as causal explanations for winning or losing.


## 12. Contextual Cricket Metrics: RAA and WAA

RAA and WAA are priority contextual metrics.

They will complement conventional batting and bowling statistics
by comparing observed outcomes with expected outcomes.

Their implementation depends on the quality and validity of
the expected-value baselines.

### 12.1 Runs Above Average (RAA)

Definition:

RAA measures actual scoring relative to an expected-runs baseline.

At delivery level:

RAA = Actual Runs - Expected Runs

For batting:

Positive RAA represents scoring above expectations.

For bowling:

The sign convention will be reversed so that positive values
represent better-than-expected run prevention.

The exact definition of actual runs must be documented.
For bowling, the scoring measure must reflect the applicable
bowler-conceded-runs rules rather than automatically treating
all team runs as runs conceded by the bowler.

### 12.2 Wickets Above Average (WAA)

Definition:

WAA measures wicket outcomes relative to expected wicket loss.

At delivery level, using the batting perspective:

WAA = Expected Wicket Loss - Actual Wicket Loss

For batting:

Positive WAA represents better-than-expected wicket preservation.

For bowling:

The sign convention will be reversed so that positive values
represent better-than-expected wicket-taking.

The expected wicket-loss baseline must be documented and validated.

Wicket credit must be distinguished from the broader wicket-event
indicator when calculating bowler performance.

### 12.3 Baseline Requirements

1. Expected values must come from a documented model.
2. Baselines must use an appropriate comparison population.
3. Match state, innings phase, and remaining resources should
   be considered where supported by the data.
4. Small-sample estimates must be treated cautiously.
5. The analysis must distinguish estimated contribution from
   causal impact.
6. RAA and WAA must be aggregated only after their delivery-level
   definitions have been validated.
7. Sign conventions must remain consistent across player,
   team, phase, and season aggregations.
8. Expected-value models must not use information that would
   be unavailable at the intended prediction point.
9. Baseline calculations must be reproducible and tested.
10. Model limitations and uncertainty must be documented.

### 12.4 Interpretation

RAA and WAA are intended to add context to conventional metrics.

They should not replace all conventional metrics or be treated
as complete measures of player quality.

Their usefulness depends on:

- The validity of the expected-value model.
- The quality of the underlying delivery data.
- The suitability of the comparison population.
- The amount of data available for each player and role.
- The consistency of the scoring and wicket definitions.

### 12.5 Implementation Priority

| Metric | Status | Dependency |
|---|---|---|
| RAA | Priority | Validated expected-runs baseline |
| WAA | Priority | Validated expected-wicket-loss baseline |
| Impact | Deferred | Validated projected-innings or resource-value model |
| WPA | Deferred | Validated win-probability model |
| Leverage | Deferred | Validated win-probability model and hypothetical outcome calculations |

Impact, WPA, and Leverage are outside the initial metric scope
unless later analysis demonstrates that they are necessary and feasible.


## 13. Feature Validation Requirements

Before a feature is accepted:

1. Its source columns and definitions must be understood.
2. Its formula must be explicitly documented.
3. Its analytical grain must be correct.
4. Its treatment of missing values must be justified.
5. Its calculations must be checked against known records.
6. Its aggregation must not double-count deliveries or matches.
7. Its denominator must be appropriate for the metric.
8. Cricket-specific rules must be respected.
9. Its limitations must be documented.
10. Its usefulness for the analytical objective must be clear.

### 13.1 Additional Metric Validation Requirements

1. Boundary Ball % and Boundary Runs % must be calculated and
   validated independently.

2. Boundary Runs % must use batter runs as its denominator.

3. Dot-ball definitions must distinguish batter runs from
   team runs.

4. Bowling Dot-ball % must use legal deliveries as its denominator.

5. Non-dot economy must use a consistent non-dot legal-delivery
   denominator and corresponding bowler-conceded runs.

6. Runs conceded and team runs must not be used interchangeably.

7. RAA and WAA must be checked against their expected-value baselines.

8. All rate metrics must have documented denominators.

9. Zero-denominator cases must be handled explicitly.

10. Feature calculations must be reproducible and covered by tests.

11. Player comparisons must consider role, phase, context,
    and sample size.

12. Shortened innings and incomplete matches must be handled explicitly.

13. The treatment of wides, no-balls, byes, leg-byes, and
    dismissal types must be documented wherever relevant.

14. The expected-value models for RAA and WAA must be validated
    before their outputs are used for scouting recommendations.

15. Feature definitions must remain consistent across seasons.


## 14. Implementation Status

The features in this document are proposed definitions.

No feature should be considered implemented or validated until
its calculation has been coded, tested, and checked against
the source data.

### 14.1 Initial Batting Metric Scope

The initial batting metrics are:

- Runs scored
- Balls faced
- Batting strike rate
- Boundary runs
- Boundary Ball %
- Boundary Runs %
- Dot-ball %
- Non-boundary Ball %, as a supplementary metric
- Dismissals
- Runs per dismissal
- Phase-specific batting metrics
- RAA
- WAA

### 14.2 Initial Bowling Metric Scope

The initial bowling metrics are:

- Runs conceded
- Legal balls bowled
- Bowling economy
- Dot-ball %
- Non-dot economy rate
- Bowler-credited wickets
- Wickets per 100 legal balls
- Boundary concession rate
- Bowling workload
- Phase-specific bowling metrics
- RAA
- WAA

### 14.3 Deferred Metrics

The following metrics are deferred:

- Impact
- Win Probability Added (WPA)
- Leverage

They may be reconsidered if later analysis demonstrates that
they are necessary, feasible, and supported by the available data.

### 14.4 Implementation Dependencies

Before implementing the features, validate:

1. The definition of legal deliveries.
2. The definition of balls faced.
3. The identification of boundary events.
4. The classification of batting dot balls.
5. The classification of bowling dot balls.
6. The calculation of bowler-conceded runs.
7. The identification of bowler-credited wickets.
8. The innings-phase boundaries.
9. The expected-runs baseline for RAA.
10. The expected-wicket-loss baseline for WAA.

### 14.5 Next Step

Validate the source-column definitions and cricket-specific
calculation rules against the actual dataset before implementing
the feature-engineering modules.

The implementation must be reproducible, testable, and aligned
with the analytical requirements of the DPL 2026 Hackathon.