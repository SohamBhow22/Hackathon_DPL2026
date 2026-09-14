# Data Quality Report

## 1. Purpose

This report documents the results of the data-quality and structural audits performed on the organiser-provided Premier League dataset.

The objective is to establish whether the dataset is suitable for reproducible statistical analysis of Kolkata Knight Riders (KKR) for the DPL 2026 Hackathon.

The audit covers:

- schema and completeness
- duplicate records
- delivery-key integrity
- match and innings structure
- shortened innings
- score and extras reconciliation
- wicket semantics
- missing tactical variables
- team-name consistency
- player identity consistency
- delivery ordering
- KKR match coverage

---

## 2. Dataset Overview

| Metric | Result |
|---|---:|
| Rows / deliveries | 34,967 |
| Columns | 61 |
| Seasons | 2023, 2024 |
| Matches | 145 |
| Competition | IPL |
| KKR matches | 28 |
| KKR matches in 2023 | 14 |
| KKR matches in 2024 | 14 |

The dataset is delivery-level, with one row representing a recorded delivery/event.

---

## 3. Schema and Completeness

The dataset contains 61 columns covering:

- match and innings identifiers
- batting and bowling players and teams
- delivery outcomes
- runs and extras
- wickets and dismissals
- innings state
- match metadata
- batting/bowling characteristics
- shot and tracking variables
- model-derived fields

The audit did not identify unexpected missingness in the primary identifiers required for delivery-level analysis.

The main missing fields are concentrated in variables where missingness has a structural or data-availability explanation.

---

## 4. Missingness Profile

The principal missing-value counts are:

| Column | Missing | Missing % |
|---|---:|---:|
| dismissal | 33,168 | 94.86% |
| inns_rrr | 18,136 | 51.87% |
| target | 18,136 | 51.87% |
| inns_runs_rem | 18,136 | 51.87% |
| bowl_speed_category | 2,379 | 6.80% |
| bowl_release_point | 2,379 | 6.80% |
| bowl_type | 1,936 | 5.54% |
| control | 963 | 2.75% |
| shot | 194 | 0.55% |
| line | 56 | 0.16% |
| length | 47 | 0.13% |

### Interpretation

These missing values should not be treated uniformly.

`inns_rrr`, `target`, and `inns_runs_rem` are second-innings-specific fields and therefore their absence in first innings is structurally expected.

`dismissal` is missing for deliveries without a wicket and therefore should not be imputed.

The tactical/tracking fields have lower levels of missingness and should be handled according to the analytical question rather than replaced indiscriminately.

**No blanket `fillna(0)` strategy is used.**

---

## 5. Duplicate and Key Integrity

Three duplicate checks were performed:

1. complete-row duplicates
2. duplicate `row_id`
3. duplicate analytical delivery key

Results:

| Check | Result |
|---|---:|
| Complete duplicate rows | 0 |
| Duplicate `row_id` | 0 |
| Duplicate `(p_match, inns, ball_id)` | 0 |

The combination:

```text
(p_match, inns, ball_id)