# DPL 2026 — Data Contract

## 1. Purpose

This document defines the rules governing how the organiser-provided
Premier League delivery-level dataset will be interpreted and used for
the DPL 2026 KKR analytical project.

The purpose of this contract is to ensure that all subsequent feature
engineering, statistical analysis, visualisations and modelling use
consistent and reproducible definitions.

The raw dataset will not be modified.

---

## 2. Source Data

The analysis uses the organiser-provided:

`Data_Premier_League_Prelims_Dataset.csv`

The dataset is a delivery-level cricket dataset covering IPL seasons
2023 and 2024.

The analysis is restricted to the organiser-provided dataset unless
additional data is explicitly documented and permitted under the
hackathon rules.

No web scraping or independently collected match data will be used to
replace or modify the organiser-provided records.

---

## 3. Analytical Grain

The fundamental analytical grain is:

**One row = one delivery event.**

The dataset contains delivery-level batting, bowling, outcome,
dismissal, tactical and tracking information.

Aggregations such as:

- innings
- match
- player
- team
- season

will be derived from the delivery-level records.

---

## 4. Delivery Key

The analytical delivery key is:

`(p_match, inns, ball_id)`

This combination uniquely identifies a delivery record in the supplied
dataset.

The `ball` column alone must not be used as a delivery key because it
represents the delivery sequence within an over rather than a globally
unique delivery identifier.

Duplicate validation of the analytical delivery key is performed by
`audit_delivery_key()`.

---

## 5. Delivery Ordering

Analytical sequencing must use:

`p_match → inns → ball_id`

The physical row order of the CSV must not be treated as the logical
match sequence.

The audit identified a match where the physical innings order differs
from the natural innings order.

Therefore, all chronological delivery-level analysis must explicitly
sort using the analytical sequencing fields rather than relying on CSV
row order.

---

## 6. Match and Innings Structure

A standard completed match is expected to contain two innings.

Matches with a different innings structure must not be silently removed.

The audit identified one match with only one recorded innings. This
record will be retained in the raw data and treated as an incomplete
match record.

Such matches must be considered explicitly when performing
match-level analyses.

---

## 7. Shortened Innings

The `max_balls` field defines the maximum number of balls applicable to
an innings.

A normal T20 innings has:

`max_balls = 120`

Values between 1 and 119 represent shortened innings and must not be
automatically treated as data errors.

max_balls = 0 is treated as an exceptional value requiring investigation and must not be interpreted as a normal zero-length innings.

Analyses involving innings duration, run rate, balls remaining or
resource utilisation must account for the applicable `max_balls`
value.

---

## 8. Score and Extras

The `score` field is treated as the authoritative delivery-level score
value.

A naïve reconciliation of:

`score = batruns + wide + noball + byes + legbyes`

does not hold for every record.

The identified reconciliation anomalies arise from overlapping
components in the supplied extras fields rather than providing
sufficient evidence that the raw `score` field itself is incorrect.

Therefore:

- raw score values will not be overwritten;
- delivery totals will not be reconstructed using the naïve equation;
- the reconciliation anomaly will be documented;
- subsequent scoring and run-rate calculations will use the
  authoritative `score` field unless a metric explicitly requires
  one of the component fields.

---

## 9. Wicket Semantics

The `out` field is the authoritative indicator of a wicket event.

For records where:

`out = True`

the dataset contains a dismissal type and dismissed-player identifier.

Therefore:

- wicket-event counts will use `out`;
- dismissal analysis will use `dismissal`;
- dismissed-player analysis will use `p_out`;
- `bat_out` must not be used as the total wicket count.

`bat_out` indicates whether the dismissed player corresponds to the
striker and may therefore differ from the number of wicket events.

This distinction is particularly important for run-outs and other
non-striker dismissal situations.

---

## 10. Missing Data

Missing values will be classified according to their analytical
meaning.

### 10.1 Structural missingness

Some missing values are expected because a field is not applicable to
every record.

Examples include:

- `target`
- `inns_runs_rem`
- `inns_rrr`

These fields are associated with second-innings chase context and must
not be globally imputed with zero.

Similarly, `dismissal` is expected to be absent when no wicket occurs.

### 10.2 Tactical/tracking missingness

Some tactical and tracking fields contain partial missingness,
including:

- `bowl_speed_category`
- `bowl_release_point`
- `bowl_type`
- `control`
- `shot`
- `line`
- `length`

These fields will not be globally imputed with zero.

Each downstream analysis must determine whether missing observations
should be excluded, grouped separately or otherwise handled based on
the meaning of the metric.

### 10.3 General rule

No blanket:

`fillna(0)`

operation will be applied to the raw dataset.

Missingness treatment must be defined at the metric/feature level.

---

## 11. Team Name Normalisation

The supplied data contains two labels referring to the same RCB
franchise:

- `Royal Challengers Bangalore`
- `Royal Challengers Bengaluru`

For analytical consistency both labels will be normalised to:

`Royal Challengers Bengaluru`

The raw dataset will remain unchanged.

Normalisation will occur only in the analytical layer.

---

## 12. Data Dictionary / CSV Naming Differences

Known naming differences between the supplied Data Dictionary and the
CSV are documented rather than silently modifying the raw schema.

| Data Dictionary | CSV |
|---|---|
| `over` | `over_num` |
| `date` | `match_date` |
| `wagonX` | `wagonx` |
| `wagonY` | `wagony` |
| `wagonZone` | `wagonzone` |

The CSV column names are treated as the authoritative names for
implementation because they represent the actual supplied dataset.

No raw-column renaming will be performed solely to make the CSV match
the Data Dictionary.

---

## 13. Player Identity

Player identifiers will be preferred over player names when joining,
grouping or tracking player records.

Where both an identifier and display name are available:

- `p_bat` is the preferred batting-player identifier;
- `p_bowl` is the preferred bowling-player identifier;
- `p_out` is the preferred dismissed-player identifier.

Player names will primarily be used for presentation and
interpretation.

---

## 14. Team and Season Analysis

Team and player analyses will preserve season context.

A player may appear for different teams across seasons.

Therefore, player-team relationships must be evaluated with season
context rather than assuming that a player's team is globally
constant.

For KKR analysis, team membership will be determined from the
match-level team fields rather than inferred solely from player names.

---

## 15. KKR Scope

The selected franchise for Question 1 is:

**Kolkata Knight Riders (KKR)**

KKR performance analysis will be conducted using the supplied records
where KKR appears as either:

- `team_bat`, or
- `team_bowl`.

Season-level comparisons will primarily focus on the 2023 and 2024
IPL seasons represented in the dataset.

The coverage of KKR matches will be validated programmatically rather
than hard-coded.

---

## 16. Raw Data Immutability

The raw CSV must remain unchanged.

All transformations, normalisations, derived variables and analytical
features must be implemented in:

- reusable Python modules under `src/`;
- notebooks under `notebooks/`;
- or explicitly generated processed outputs.

This preserves traceability from analytical results back to the
organiser-provided data.

---

## 17. Reproducibility

Every major analytical result must be reproducible from the repository.

Where custom metrics, statistical methods or models are introduced,
their definitions and assumptions must be documented.

The analysis should avoid undocumented manual corrections to the raw
data.

The repository therefore follows the principle:

**Raw data → validated analytical rules → derived features →
analysis → visualisation → recommendations**

---

## 18. Analytical Implications

The following principles will govern subsequent KKR analysis:

1. Delivery-level metrics must use the validated delivery key.
2. Delivery sequencing must not depend on physical CSV order.
3. Wickets must be counted using `out`, not `bat_out`.
4. Raw `score` must be used for delivery-level scoring calculations.
5. Shortened innings must be recognised before comparing innings-level
   rates or totals.
6. Structural missingness must not be interpreted as zero.
7. Tactical analyses must report or account for missing observations.
8. Team-name normalisation must occur before cross-team comparisons.
9. Season context must be retained for player/team analysis.
10. Raw data must remain unchanged.

---

## 19. Validation

The rules defined in this contract are supported by the project audit
functions and automated tests.

The audit test suite validates:

- delivery-key uniqueness;
- duplicate-key detection;
- RCB name normalisation;
- RCB variant detection;
- wicket-field semantics;
- incomplete-match detection;
- shortened-innings handling;
- delivery-order anomalies;
- Data Dictionary/CSV naming mappings.

These tests form part of the reproducibility layer of the project.