"""Reusable metric definitions for delivery-level IPL analytics.

The functions in this module derive analytical features without modifying
the input DataFrame.

Important:
- The raw dataset must remain unchanged.
- Batting dot balls remain a provisional definition.
- Source bowlruns anomalies must not be silently corrected.
"""

from __future__ import annotations
from unittest import result

import pandas as pd


# Dismissals included in the candidate bowler-credited wicket metric.
BOWLER_CREDITED_DISMISSALS = {
    "caught",
    "bowled",
    "leg before wicket",
    "stumped",
    "hit wicket",
}


def derive_legal_delivery(df: pd.DataFrame) -> pd.Series:
    """Return whether each delivery is legal.

    A delivery is legal when neither a wide nor a no-ball is recorded.
    """
    required_columns = {"wide", "noball"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing columns for legal-delivery calculation: "
            f"{sorted(missing_columns)}"
        )

    return (
        df["wide"].eq(0)
        & df["noball"].eq(0)
    ).fillna(False).astype(bool)


def derive_batting_dot(df: pd.DataFrame) -> pd.Series:
    """Return the provisional batting dot-ball indicator.

    A candidate batting dot ball is recorded as a ball faced on which
    the batter scores zero runs.

    This definition remains provisional pending edge-case review.
    """
    required_columns = {"ballfaced", "batruns"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing columns for batting dot-ball calculation: "
            f"{sorted(missing_columns)}"
        )

    return (
        df["ballfaced"].eq(1)
        & df["batruns"].eq(0)
    ).fillna(False).astype(bool)


def derive_bowling_dot(
    df: pd.DataFrame,
    legal_delivery: pd.Series | None = None,
) -> pd.Series:
    """Return whether each delivery is a bowling dot ball.

    A bowling dot ball is a legal delivery on which the recorded
    team score is zero.

    An optional precomputed legal_delivery Series can be supplied.
    """
    if "score" not in df.columns:
        raise ValueError(
            "Missing columns for bowling dot-ball calculation: ['score']"
        )

    if legal_delivery is None:
        legal_delivery = derive_legal_delivery(df)

    if not legal_delivery.index.equals(df.index):
        raise ValueError(
            "legal_delivery index must match the DataFrame index."
        )

    return (
        legal_delivery
        & df["score"].eq(0)
    ).fillna(False).astype(bool)


def derive_bowler_credited_wicket(df: pd.DataFrame) -> pd.Series:
    """Return the candidate bowler-credited wicket indicator.

    A record qualifies when:
    - out is True; and
    - dismissal belongs to BOWLER_CREDITED_DISMISSALS.

    This classification follows the validated source labels. It does
    not independently verify each dismissal against an official scorecard.
    """
    required_columns = {"out", "dismissal"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing columns for bowler-credited wicket calculation: "
            f"{sorted(missing_columns)}"
        )

    return (
        df["out"].eq(True)
        & df["dismissal"].isin(BOWLER_CREDITED_DISMISSALS)
    ).fillna(False).astype(bool)


def derive_match_phase(df: pd.DataFrame) -> pd.Series:
    """Assign an initial T20 phase using one-based over numbering.

    Powerplay: overs 1–6
    Middle:    overs 7–15
    Death:     overs 16–20

    Missing, non-integer, or out-of-range over numbers receive <NA>.
    """
    if "over_num" not in df.columns:
        raise ValueError(
            "Missing columns for match-phase calculation: ['over_num']"
        )

    # Coerce invalid values to missing rather than assigning them a phase.
    over_num = pd.to_numeric(df["over_num"], errors="coerce")

    # Only whole-number over values from 1 through 20 are valid.
    valid_over = (
        over_num.notna()
        & over_num.between(1, 20)
        & over_num.mod(1).eq(0)
    )

    phase = pd.Series(
        pd.NA,
        index=df.index,
        dtype="string",
        name="match_phase",
    )

    phase.loc[valid_over & over_num.between(1, 6)] = "Powerplay"
    phase.loc[valid_over & over_num.between(7, 15)] = "Middle"
    phase.loc[valid_over & over_num.between(16, 20)] = "Death"

    return phase


def add_metric_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the DataFrame with the derived metric features.

    The original DataFrame is not modified.
    """
    result = df.copy()

    result["legal_delivery"] = derive_legal_delivery(result)
    result["batting_dot"] = derive_batting_dot(result)
    result["bowling_dot"] = derive_bowling_dot(
        result,
        legal_delivery=result["legal_delivery"],
    )
    result["bowler_credited_wicket"] = (
        derive_bowler_credited_wicket(result)
    )
    result["match_phase"] = derive_match_phase(result)
    result["boundary_ball"] = derive_boundary_ball(result)
    result["boundary_runs"] = derive_boundary_runs(result)
    result["wides"] = derive_wides(result)
    result["noball_extras"] = derive_noball_extras(result)
    result["wide_noball_extras"] = derive_wide_noball_extras(result)

    return result


def derive_boundary_ball(df: pd.DataFrame) -> pd.Series:
    """Identify balls on which the batter scores four or six off the bat."""
    required = {"ballfaced", "batruns"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    return (
        df["ballfaced"].eq(1)
        & df["batruns"].isin([4, 6])
    ).fillna(False).astype(bool)


def derive_boundary_runs(df: pd.DataFrame) -> pd.Series:
    """Return batter runs scored on deliveries yielding four or six off the bat."""
    required = {"batruns"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    return df["batruns"].where(
        df["batruns"].isin([4, 6]),
        0,
    )

def derive_wides(df: pd.DataFrame) -> pd.Series:
    """Return the recorded wide extras for each delivery."""
    if "wide" not in df.columns:
        raise ValueError("Missing required columns: ['wide']")

    return df["wide"].fillna(0)


def derive_noball_extras(df: pd.DataFrame) -> pd.Series:
    """Return the recorded no-ball extras for each delivery."""
    if "noball" not in df.columns:
        raise ValueError("Missing required columns: ['noball']")

    return df["noball"].fillna(0)


def derive_wide_noball_extras(df: pd.DataFrame) -> pd.Series:
    """Return combined wide and no-ball extras for each delivery."""
    return derive_wides(df) + derive_noball_extras(df)