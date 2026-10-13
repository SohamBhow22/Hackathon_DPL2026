"""Build player-level analytical datasets from delivery records."""

from __future__ import annotations

import pandas as pd


# Grouping keys defining each analytical dataset.
PLAYER_SEASON_BATTING_KEYS = [
    "p_bat",
    "year",
]

PLAYER_SEASON_BOWLING_KEYS = [
    "p_bowl",
    "year",
]

PLAYER_SEASON_PHASE_BATTING_KEYS = [
    "p_bat",
    "year",
    "match_phase",
]

PLAYER_SEASON_PHASE_BOWLING_KEYS = [
    "p_bowl",
    "year",
    "match_phase",
]


def build_player_season_batting(
        
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Build one row per batter per season."""

    required_columns = {
        "p_bat",
        "bat",
        "year",
        "batruns",
        "ballfaced",
        "batting_dot",
        "boundary_ball",
        "boundary_runs",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Aggregate the underlying counts at player-season grain.
    batting = (
        df.groupby(
            PLAYER_SEASON_BATTING_KEYS,
            as_index=False,
            dropna=False,
        )
        .agg(
            batter_name=("bat", "first"),
            runs=("batruns", "sum"),
            balls_faced=("ballfaced", "sum"),
            dot_balls=("batting_dot", "sum"),
            boundary_balls=("boundary_ball", "sum"),
            boundary_runs=("boundary_runs", "sum")
        )
    )

    # Calculate rates from aggregated counts.
    batting["strike_rate"] = (
        batting["runs"]
        .div(batting["balls_faced"].where(batting["balls_faced"] != 0))
        .mul(100)
    )

    batting["dot_ball_pct"] = (
        batting["dot_balls"]
        .div(batting["balls_faced"].where(batting["balls_faced"] != 0))
        .mul(100)
    )
    batting["boundary_ball_pct"] = (
        batting["boundary_balls"]
        .div(
            batting["balls_faced"].where(
                batting["balls_faced"] != 0
            )
        )
        .mul(100)
    )

    batting["boundary_run_pct"] = (
        batting["boundary_runs"]
        .div(
            batting["runs"].where(
                batting["runs"] != 0
            )
        )
        .mul(100)
    )

    # Enforce the expected analytical grain.
    if batting.duplicated(PLAYER_SEASON_BATTING_KEYS).any():
        raise ValueError(
            "Player-season batting dataset contains duplicate keys."
        )

    return batting


def build_player_season_bowling(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Build one row per bowler per season."""

    required_columns = {
        "p_bowl",
        "bowl",
        "year",
        "bowlruns",
        "legal_delivery",
        "bowling_dot",
        "bowler_credited_wicket",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Aggregate counts at player-season grain.
    bowling = (
        df.groupby(
            PLAYER_SEASON_BOWLING_KEYS,
            as_index=False,
            dropna=False,
        )
        .agg(
            bowler_name=("bowl", "first"),
            runs_conceded=("bowlruns", "sum"),
            legal_balls=("legal_delivery", "sum"),
            dot_balls=("bowling_dot", "sum"),
            wickets=("bowler_credited_wicket", "sum"),
        )
    )

    # Calculate rates from aggregated counts.
    valid_legal_balls = bowling["legal_balls"].where(
        bowling["legal_balls"] != 0
    )

    bowling["economy_rate"] = (
        bowling["runs_conceded"]
        .div(valid_legal_balls)
        .mul(6)
    )

    bowling["bowling_dot_pct"] = (
        bowling["dot_balls"]
        .div(valid_legal_balls)
        .mul(100)
    )

    bowling["wickets_per_100_balls"] = (
        bowling["wickets"]
        .div(valid_legal_balls)
        .mul(100)
    )

    # Enforce the expected analytical grain.
    if bowling.duplicated(PLAYER_SEASON_BOWLING_KEYS).any():
        raise ValueError(
            "Player-season bowling dataset contains duplicate keys."
        )

    return bowling

def build_player_season_phase_batting(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Build one row per batter, season, and match phase."""

    required_columns = {
        "p_bat",
        "bat",
        "year",
        "match_phase",
        "batruns",
        "ballfaced",
        "batting_dot",
        "boundary_ball",
        "boundary_runs",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Aggregate underlying counts at player-season-phase grain.
    batting = (
        df.groupby(
            PLAYER_SEASON_PHASE_BATTING_KEYS,
            as_index=False,
            dropna=False,
        )
        .agg(
            batter_name=("bat", "first"),
            runs=("batruns", "sum"),
            balls_faced=("ballfaced", "sum"),
            dot_balls=("batting_dot", "sum"),
            boundary_balls=("boundary_ball", "sum"),
            boundary_runs=("boundary_runs", "sum"),
        )
    )

    # Calculate rates from aggregated counts.
    valid_balls = batting["balls_faced"].where(
        batting["balls_faced"] != 0
    )

    batting["strike_rate"] = (
        batting["runs"].div(valid_balls).mul(100)
    )

    batting["dot_ball_pct"] = (
        batting["dot_balls"].div(valid_balls).mul(100)
    )

    batting["boundary_ball_pct"] = (
        batting["boundary_balls"].div(valid_balls).mul(100)
    )

    valid_runs = batting["runs"].where(
        batting["runs"] != 0
    )

    batting["boundary_run_pct"] = (
        batting["boundary_runs"].div(valid_runs).mul(100)
    )

    # Enforce the expected analytical grain.
    if batting.duplicated(
        PLAYER_SEASON_PHASE_BATTING_KEYS
    ).any():
        raise ValueError(
            "Player-season-phase batting dataset contains duplicate keys."
        )

    return batting


def build_player_season_phase_bowling(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Build one row per bowler, season, and match phase."""

    required_columns = {
        "p_bowl",
        "bowl",
        "year",
        "match_phase",
        "bowlruns",
        "legal_delivery",
        "bowling_dot",
        "bowler_credited_wicket",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Aggregate counts at player-season-phase grain.
    bowling = (
        df.groupby(
            PLAYER_SEASON_PHASE_BOWLING_KEYS,
            as_index=False,
            dropna=False,
        )
        .agg(
            bowler_name=("bowl", "first"),
            runs_conceded=("bowlruns", "sum"),
            legal_balls=("legal_delivery", "sum"),
            dot_balls=("bowling_dot", "sum"),
            wickets=("bowler_credited_wicket", "sum"),
        )
    )

    # Calculate rates from aggregated counts.
    valid_legal_balls = bowling["legal_balls"].where(
        bowling["legal_balls"] != 0
    )

    bowling["economy_rate"] = (
        bowling["runs_conceded"]
        .div(valid_legal_balls)
        .mul(6)
    )

    bowling["bowling_dot_pct"] = (
        bowling["dot_balls"]
        .div(valid_legal_balls)
        .mul(100)
    )

    bowling["wickets_per_100_balls"] = (
        bowling["wickets"]
        .div(valid_legal_balls)
        .mul(100)
    )

    # Enforce the expected analytical grain.
    if bowling.duplicated(
        PLAYER_SEASON_PHASE_BOWLING_KEYS
    ).any():
        raise ValueError(
            "Player-season-phase bowling dataset contains duplicate keys."
        )

    return bowling