**# Metric Definition Validation — KKR IPL Analytics**



**## 1. Purpose**



This document records the validation of source columns and

calculation rules required for the KKR IPL analytics project.



The objective is to establish which metrics can be calculated

directly from the supplied dataset, which require transformations,

and which require further investigation.



The validation uses:



\- Data_Premier_League_Prelims_Dataset.csv

\- Data_Dictionary.pdf

\- Existing data-quality audit findings



No raw data values are modified as part of this validation.



**## 2. Source Columns**



\| Column | Intended use | Validation status |

\|---|---|---|

\| score | Total runs scored from a delivery | Use as the authoritative recorded team score |

\| batruns | Runs credited to the batter | Suitable for batting-run aggregation |

\| ballfaced | Whether a delivery counts as a ball faced | Use for batting denominators after validation |

\| outcome | Delivery outcome category | Suitable for identifying recorded fours and sixes |

\| wide | Wide runs recorded on a delivery | Use with the validated extras rules |

\| noball | No-ball indicator | Use with the validated extras rules |

\| byes | Bye runs | Required for extras analysis |

\| legbyes | Leg-bye runs | Required for extras analysis |

\| bowlruns | Runs charged to the bowler | Intended source for bowling runs conceded; anomalies require investigation |

\| out | Whether a wicket fell | Authoritative wicket-event indicator |

\| dismissal | Recorded dismissal type | Use to classify wicket events |

\| p_out | Player identifier associated with a dismissal | Use only on validated wicket-event records |

\| over_num | Over number | Validate numbering before assigning phases |

\| predscore | Model-predicted final innings score | Potential input to contextual analysis; semantics require further validation |

\| wprob | Model-estimated win probability of the batting team | Not an expected-wicket-loss measure |



**## 3. Batting Metric Decisions**



**### 3.1 Balls Faced**



Source column:



ballfaced



Definition:



Use the supplied ballfaced indicator to count balls faced.



Calculation:



Balls Faced = Sum of ballfaced



Validation findings:



\- Total delivery records: 34,967

\- Records with ballfaced = 1: 33,612

\- Records with ballfaced = 0: 1,355

\- All 1,355 records with ballfaced = 0 have a nonzero wide value.

\- All 175 records with noball = 1 have ballfaced = 1.



Decision:



Use ballfaced for the batting denominator rather than reconstructing

balls faced from the outcome category.



Balls faced and legal deliveries must not be treated as equivalent.



**### 3.2 Boundary Events**



Source columns:



\- outcome

\- batruns



Validation findings:



\- Recorded four outcomes: 4,348

\- Recorded six outcomes: 2,384

\- All four outcomes have batruns = 4.

\- All six outcomes have batruns = 6.



Decision:



Use validated outcome categories to identify boundary-scoring balls.



Boundary Ball %:



Boundary-scoring balls / Balls Faced \* 100



Boundary Runs %:



Batter runs from fours and sixes / Total batter runs \* 100



Boundary Runs % must use batter runs, not total team runs,

as its denominator.



If total batter runs are zero, Boundary Runs % is undefined.



**### 3.3 Dot-Ball Definitions**



Batting Dot-ball %:



Count balls faced on which the batter scores zero batter runs,

using a documented definition consistent across the analysis.



Bowling Dot-ball %:



Count legal deliveries on which the batting team scores zero total runs.



The two definitions are different.



A delivery producing byes or leg-byes may count as a batting

dot ball because the batter scores zero, but it is not a

bowling dot ball because the team scores runs.



A wide does not count as a ball faced in the supplied data.



The implementation must explicitly validate the treatment of

no-balls and other extras.



**## 4. Bowling Metric Decisions**



**### 4.1 Legal Deliveries**



Proposed definition:



A delivery is legal when:



\- wide = 0

\- noball = 0



Validation findings:



\- Total delivery records: 34,967

\- Wide records: 1,355

\- No-ball records: 175

\- No delivery has both a nonzero wide value and noball = 1.

\- Candidate legal deliveries: 33,437



This definition must be retained consistently across bowling

economy, bowling Dot-ball %, and wickets per 100 legal balls.



**### 4.2 Runs Conceded**



Source column:



bowlruns



The data dictionary defines bowlruns as runs charged against

the bowler, including wides and no-balls but excluding byes

and leg-byes.



Validation finding:



Six records have `bowlruns = -3`. These records involve a no-ball

and four byes or four leg-byes. A broader comparison against the

candidate formula `batruns + wide + noball` identified 14 mismatches

in total: 8 records where the source is one run lower and 6 where it

is four runs lower. All 14 involve a no-ball and nonzero byes or leg-byes.



Additionally, the following relationship holds for all records:



score = bowlruns + byes + legbyes



Decision:



Retain bowlruns as the intended source column, but investigate

the six negative values before accepting the field without qualification.



Do not silently replace negative values or exclude affected records.



**### 4.3 Bowling Economy**



Proposed formula:



Bowling Economy =

Total Bowler-Conceded Runs / Legal Deliveries \* 6



The treatment of anomalous bowlruns records must be resolved

before finalising the implementation.



**### 4.4 Bowling Dot-Ball %**



Proposed formula:



Bowling Dot-ball % =

Legal Deliveries with score = 0 / Legal Deliveries \* 100



Use total team scoring, rather than batter runs alone,

to determine whether a delivery is a bowling dot ball.



**### 4.5 Non-Dot Economy Rate**



Proposed formula:



Non-dot Economy Rate =

Bowler-Conceded Runs on Non-Dot Legal Deliveries

/ Non-Dot Legal Deliveries \* 6



A non-dot legal delivery is a legal delivery on which the

batting team scores at least one run.



The numerator must use bowler-conceded runs rather than

automatically using total team runs.



The treatment of anomalous bowler-conceded-run values must

be resolved before final implementation.



If the denominator is zero, the rate is undefined.



**### 4.6 Investigation of Bowling-Runs Anomalies**



The candidate calculation



candidate_bowlruns = batruns + wide + noball



was compared against the supplied bowlruns column.



Results:



\- 34,953 records match the candidate calculation.

\- 8 records have bowlruns one run below the candidate.

\- 6 records have bowlruns four runs below the candidate.

\- All 14 mismatches involve a no-ball and nonzero byes or leg-byes.



On all 14 records, the recorded score is 1 despite the recorded

scoring components implying either 2 or 5 team runs.



The source fields therefore contain a scoring-component inconsistency.



The reconciliation



score = bowlruns + byes + legbyes



does not independently validate the values because bowlruns

reconciles the other components to the recorded score.



Decision:



\- Preserve the raw dataset unchanged.

\- Do not silently replace score or bowlruns.

\- Investigate the effect on KKR's bowling metrics.

\- If the candidate formula is adopted, create a separate

&#x20; analytical field and document its assumptions.

\- Report the unresolved source-data discrepancy.



**### 4.7 Impact on KKR Bowling Metrics**



The 14 mismatches were further analysed to quantify their

impact on KKR's bowling statistics.



Across the full dataset:



\- Total mismatches: 14

\- Mismatches when KKR was bowling: 2

\- Mismatches when KKR was batting: 3



The two KKR bowling mismatches occurred in 2024:



\| Bowler | Source runs | Candidate runs | Legal balls |

\|---|---:|---:|---:|

\| Vaibhav Arora | 418 | 422 | 276 |

\| Varun Chakravarthy | 827 | 831 | 616 |



The aggregate economy comparison is:



\| Bowler | Source economy | Candidate economy |

\|---|---:|---:|

\| Vaibhav Arora | 9.087 | 9.174 |

\| Varun Chakravarthy | 8.055 | 8.094 |



The candidate calculation increases aggregate economy by

approximately 0.087 runs per over for Vaibhav Arora and

0.039 runs per over for Varun Chakravarthy.



These figures aggregate the available 2023 and 2024 records.



Decision:



\- Preserve the original bowlruns values.

\- Do not silently overwrite the source data.

\- Retain the candidate calculation as a separate analytical

&#x20; alternative pending final validation.

\- Document the 14 source-data inconsistencies.

\- State the chosen calculation explicitly when presenting

&#x20; bowling metrics.



**## 5. Wicket Semantics**



Source columns:



\- out

\- dismissal

\- p_out

\- bat_out



Decision:



Use out as the authoritative wicket-event indicator.



Use dismissal to identify the type of dismissal.



Use p_out only on validated wicket-event records.



Do not infer a wicket solely from p_out or bat_out.



The bowler-credited wicket calculation must distinguish

dismissals credited to the bowler from those that are not.



The applicable dismissal rules must be documented before

implementing bowler wicket totals and WAA.



**## 6. Contextual Metrics**



**### 6.1 Runs Above Average (RAA)**



RAA requires a validated expected-runs baseline.



The predscore field contains a model-predicted final innings

score, but it must not automatically be treated as the

expected runs from an individual delivery.



Further investigation is required to determine whether predscore

can support the intended RAA methodology.



**### 6.2 Wickets Above Average (WAA)**



WAA requires a validated expected-wicket-loss baseline.



The wprob field represents estimated win probability and is

not an expected-wicket-loss probability.



Therefore, wprob must not be used directly as the WAA baseline.



A separate expected-wicket-loss model or defensible estimation

method is required.



**### 6.3 Implementation Status**



RAA and WAA remain priority metrics, but their implementation

depends on validating the expected-value baselines.



No contextual metric should be treated as validated merely

because a source column with a related name exists.



**## 7. Outstanding Investigations**

The following items remain open or require follow-up:

| Investigation | Current status | Next action |
|---|---|---|
| Negative and inconsistent `bowlruns` values | Open | Retain source values; investigate the 14 no-ball/extras inconsistencies before finalising economy metrics. |
| Treatment of wides and no-balls | Core legal-delivery rule validated | Use `wide == 0` and `noball == 0` for legal deliveries; preserve the distinct `ballfaced` definition. |
| Batting dot-ball definition | Provisional | Review unusual dismissal/retirement edge cases before finalising. |
| Bowling dot-ball definition | Validated for initial analysis | Use legal deliveries with `score == 0`. |
| Bowler-credited wicket classification | Validated against source dismissal labels | Use the five documented dismissal types; keep source `out` and `bat_out` semantics distinct. |
| Over-numbering and phase boundaries | Validated for initial analysis | Use one-based `over_num` values 1–20 and the documented T20 phase buckets; account for shortened/incomplete innings. |
| `predscore` suitability for RAA | Open | Establish whether it can support a defensible expected-runs baseline at the required delivery-level grain. |
| Expected-wicket-loss baseline for WAA | Open | Develop and validate a separate expected-wicket-loss model or defensible estimation method. |
| Source scorecard verification | Not performed | Independently verify unusual source records against authoritative match records if those records are available. |

Completed validation checks should not be treated as unresolved simply because their definitions still require implementation and automated tests.


**## 8. Reproducibility**



All metric calculations must be implemented through reproducible

code and validated with automated tests.



The raw dataset must remain unchanged.



Any exclusions, corrections, assumptions, or alternative

calculations must be documented explicitly.

**## 9. Latest Validation Results — Delivery, Wicket and Phase Definitions**

This section records the outcomes of subsequent notebook checks. Where an earlier section described a definition as proposed or pending, the statuses below reflect the latest validation state. The raw dataset remains unchanged.

**### 9.1 Legal Deliveries**

**Status:** Validated against dataset patterns.

A delivery is treated as legal when `wide == 0` and `noball == 0`.

```python
df["legal_delivery"] = (
    df["wide"].eq(0)
    & df["noball"].eq(0)
)
```

| Metric | Count |
|---|---:|
| Total delivery records | 34,967 |
| Legal deliveries | 33,437 |
| Illegal deliveries | 1,530 |
| `ballfaced = 0` | 1,355 |
| `ballfaced = 1` | 33,612 |
| No-balls with `ballfaced = 1` | 175 |

| `legal_delivery` | `ballfaced = 0` | `ballfaced = 1` | Total |
|---|---:|---:|---:|
| False | 1,355 | 175 | 1,530 |
| True | 0 | 33,437 | 33,437 |
| **Total** | **1,355** | **33,612** | **34,967** |

No records had both a nonzero `wide` value and a nonzero `noball` value.

**Decision:** Use `legal_delivery` for legal-ball counts and bowling denominators. Do not substitute `ballfaced` for legal deliveries: 175 no-balls have `ballfaced = 1`.

**### 9.2 Bowling Dot Balls**

**Status:** Definition accepted for initial analysis.

A bowling dot ball is a legal delivery on which the recorded team score is zero:

```python
df["bowling_dot"] = (
    df["legal_delivery"]
    & df["score"].eq(0)
)
```

| Metric | Count |
|---|---:|
| Bowling dot-ball records | 11,186 |
| Legal deliveries with nonzero team score | 22,251 |
| Illegal deliveries with zero team score | 0 |

Legal deliveries can produce byes or leg-byes even when `batruns = 0`. Those deliveries are not bowling dot balls because the team has scored runs.

`Bowling dot-ball % = Bowling dot balls / Legal deliveries × 100`

The numerator and denominator must use the same analytical scope, such as the same bowler, innings, match, or phase.

**### 9.3 Batting Dot Balls**

**Status:** Provisional; edge-case review remains open.

Candidate definition:

```python
df["batting_dot"] = (
    df["ballfaced"].eq(1)
    & df["batruns"].eq(0)
)
```

This definition produces 11,808 candidate batting dot-ball records.

The candidate set includes dismissal events: 268 bowled, 1,270 caught, 1 hit wicket, 115 LBW, 2 retired-not-out (hurt), 1 retired out, 56 run outs, and 26 stumpings. A dismissal can occur on a delivery on which the batter scores zero, so the presence of a dismissal is not by itself a reason to exclude a batting dot ball.

However, the two records labelled `retired not out (hurt)` are marked `out = True` in the source. Retain this inconsistency in the audit trail.

**Decision:** Keep the candidate definition for exploratory analysis, but review edge cases before treating it as fully validated. Batting dot balls and bowling dot balls are distinct metrics.

**### 9.4 Wicket Events and Bowler-Credited Wickets**

**Status:** Candidate bowler-credited classification validated against source dismissal labels and bowler identity presence.

The source contains 1,799 records with `out = True`.

| Metric | Count |
|---|---:|
| Records marked `out = True` | 1,799 |
| Records with `out = True` and `bat_out = True` | 1,747 |
| Records with `out = True` and `bat_out = False` | 52 |
| Candidate bowler-credited wickets | 1,687 |
| Candidate wickets with missing bowler | 0 |
| Candidate wickets with blank bowler | 0 |

Use the following dismissal set for the candidate bowler-credited wicket measure:

```python
BOWLER_CREDITED_DISMISSALS = {
    "caught",
    "bowled",
    "leg before wicket",
    "stumped",
    "hit wicket",
}

df["bowler_credited_wicket"] = (
    df["out"].eq(True)
    & df["dismissal"].isin(BOWLER_CREDITED_DISMISSALS)
)
```

| Dismissal type | Source records marked `out = True` | Candidate bowler-credited |
|---|---:|---:|
| Caught | 1,270 | 1,270 |
| Bowled | 268 | 268 |
| Leg before wicket | 115 | 115 |
| Run out | 107 | 0 |
| Stumped | 33 | 33 |
| Retired not out (hurt) | 2 | 0 |
| Retired out | 2 | 0 |
| Hit wicket | 1 | 1 |
| Obstructing the field | 1 | 0 |
| **Total** | **1,799** | **1,687** |

No `out = True` records had a missing dismissal type. The 112 records excluded from the candidate bowler-credited classification comprise 107 run outs, 2 retired-not-out (hurt), 2 retired-out, and 1 obstructing-the-field record.

**Decision:** Use the documented five-type set for provisional bowler-credited wicket counts. Do not substitute `bat_out` for `out`. The two retired-not-out (hurt) records marked `out = True` remain a source-data inconsistency. This check validates consistency with the available labels and the presence of bowler identities; it does not independently verify every dismissal against an original scorecard.

`Wickets per 100 legal deliveries = Bowler-credited wickets / Legal deliveries × 100`

The numerator and denominator must be scoped to the same bowler, innings, match, or phase population.

**### 9.5 Over Numbering and T20 Phases**

**Status:** Over-number convention validated; phase definitions adopted for initial analysis.

The observed `over_num` range is 1–20, indicating one-based over numbering.

| Phase | `over_num` | Number of overs |
|---|---|---:|
| Powerplay | 1–6 | 6 |
| Middle overs | 7–15 | 9 |
| Death overs | 16–20 | 5 |

**Decision:** Use these boundaries for initial T20 phase analysis. Before comparing phase metrics across matches, account for incomplete innings, shortened innings, and innings ending before the 20th over. Fewer records in later overs are not, by themselves, proof of missing data.

Calculate phase metrics from underlying delivery records. Do not average rates across groups without considering their denominators.

**### 9.6 Updated Bowling-Runs Anomaly Status**

The candidate calculation `batruns + wide + noball` matches the supplied `bowlruns` value on 34,953 records and differs on 14 records. Eight records have the source value one run below the candidate; six have it four runs below the candidate. All 14 involve a no-ball and nonzero byes or leg-byes.

The six `bowlruns = -3` records are a subset of those 14 mismatches, not the full anomaly set.

The KKR bowling impact remains:

| Bowler | Source runs | Candidate runs | Legal balls | Source economy | Candidate economy |
|---|---:|---:|---:|---:|---:|
| Vaibhav Arora | 418 | 422 | 276 | 9.087 | 9.174 |
| Varun Chakravarthy | 827 | 831 | 616 | 8.055 | 8.094 |

**Decision:** Preserve raw `score` and `bowlruns`; do not silently correct either. Retain any alternative calculation as a separately named analytical field with its assumptions documented. The inconsistency remains open until independently resolved.

**### 9.7 Implementation and Test Requirements**

Implement the validated or provisionally accepted definitions in reproducible feature-engineering code and protect them with automated tests.

Tests should cover:
- Legal-delivery classification.
- Bowling dot-ball classification.
- The provisional batting dot-ball definition and its edge cases.
- Bowler-credited dismissal classification.
- Presence of bowler identities on candidate bowler-credited wickets.
- One-based over numbering and phase boundaries.
- Preservation and monitoring of the 14 `bowlruns` mismatches.

The observed counts are regression checks for the current dataset, not universal constants for future datasets.

Raw source data must remain immutable. Any exclusions, corrections, assumptions, or alternative calculations must be documented explicitly.
