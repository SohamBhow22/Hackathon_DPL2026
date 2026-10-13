"""Build match-level and team-match datasets from delivery records."""

from __future__ import annotations

import pandas as pd


MATCH_COLUMNS = [
    "p_match",
    "year",
    "match_date",
    "ground",
    "country",
    "winner",
    "toss",
]

TEAM_COLUMNS = [
    "team_bat",
    "team_bowl",
]

# Map alternative source names to a single canonical team name.
# The raw dataset remains unchanged.
TEAM_NAME_MAPPING = {
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
}


def standardise_team_name(value: object) -> object:
    """Return a canonical team name without modifying the source data."""
    if not isinstance(value, str):
        return value

    cleaned_value = value.strip()

    if cleaned_value in {"", "-"}:
        return cleaned_value

    return TEAM_NAME_MAPPING.get(cleaned_value, cleaned_value)


def _single_value(series: pd.Series) -> object:
    """Return the sole distinct non-null value, or None if ambiguous."""
    values = series.dropna().unique()

    if len(values) == 1:
        return values[0]

    return None


def _canonical_team_set(series: pd.Series) -> set[str]:
    """Return distinct, non-null team names in canonical form."""
    return {
        standardise_team_name(team)
        for team in series.dropna().unique()
        if isinstance(standardise_team_name(team), str)
        and standardise_team_name(team).strip() not in {"", "-"}
    }


def _canonical_winner(series: pd.Series) -> object:
    """Return the canonical winner, preserving missing/unclassified values."""
    winner = _single_value(series)

    if winner is None:
        return None

    if not isinstance(winner, str):
        return winner

    return standardise_team_name(winner)


def build_match_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Create one record per match and report metadata inconsistencies."""
    required = set(MATCH_COLUMNS + TEAM_COLUMNS + ["inns"])
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    records = []

    for match_id, group in df.groupby("p_match", sort=True):
        record = {"p_match": match_id}

        # Collect one value for each match-level metadata field.
        for column in MATCH_COLUMNS:
            if column == "p_match":
                continue

            if column == "winner":
                record[column] = _canonical_winner(group[column])
            else:
                record[column] = _single_value(group[column])

        # Standardise team identities before counting represented teams.
        batting_teams = _canonical_team_set(group["team_bat"])
        bowling_teams = _canonical_team_set(group["team_bowl"])

        represented_teams = batting_teams | bowling_teams

        record["represented_batting_teams"] = len(batting_teams)
        record["represented_bowling_teams"] = len(bowling_teams)
        record["represented_teams"] = len(represented_teams)
        record["represented_innings"] = group["inns"].nunique()

        record["single_batting_team_flag"] = len(batting_teams) < 2

        # Standardise team-name fields before checking for conflicts.
        # This prevents known aliases from creating false conflicts.
        metadata_conflicts = []

        for column in MATCH_COLUMNS:
            if column == "p_match":
                continue

            values = group[column].dropna()

            if column in {"winner", "toss"}:
                values = values.map(standardise_team_name)

            if values.nunique() > 1:
                metadata_conflicts.append(column)

        record["metadata_conflict_flag"] = bool(metadata_conflicts)

        winner = record["winner"]

        record["result_class"] = (
            "unclassified"
            if winner is None
            or not isinstance(winner, str)
            or winner.strip() in {"", "-"}
            else "classified"
        )

        records.append(record)

    result = pd.DataFrame(records)

    if result["p_match"].duplicated().any():
        raise ValueError(
            "Match summary contains duplicate match IDs."
        )

    return result


def build_team_match(
    df: pd.DataFrame,
    match_summary: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Create one record per represented team per match."""
    required = {
        "p_match",
        "team_bat",
        "team_bowl",
        "winner",
    }
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    if match_summary is None:
        match_summary = build_match_summary(df)

    required_summary_columns = {
        "p_match",
        "year",
        "winner",
        "result_class",
    }
    missing_summary = required_summary_columns - set(match_summary.columns)

    if missing_summary:
        raise ValueError(
            "Missing required match-summary columns: "
            f"{sorted(missing_summary)}"
        )

    if match_summary["p_match"].duplicated().any():
        raise ValueError(
            "Match summary contains duplicate match IDs."
        )

    # Use the canonical winner from the match summary.
    match_metadata = match_summary[
        ["p_match", "year", "winner", "result_class"]
    ].copy()

    team_records = []

    for match_id, group in df.groupby("p_match", sort=True):
        teams = (
            _canonical_team_set(group["team_bat"])
            | _canonical_team_set(group["team_bowl"])
        )

        winner = _canonical_winner(group["winner"])

        for team in sorted(teams):
            opponents = teams - {team}

            if len(opponents) == 1:
                opponent = next(iter(opponents))
            else:
                opponent = pd.NA

            if (
                winner is None
                or not isinstance(winner, str)
                or winner.strip() in {"", "-"}
            ):
                team_result = "unclassified"
            elif winner == team:
                team_result = "win"
            elif winner in opponents:
                team_result = "loss"
            else:
                team_result = "unresolved"

            team_records.append(
                {
                    "p_match": match_id,
                    "team": team,
                    "opponent": opponent,
                    "winner": winner,
                    "team_result": team_result,
                }
            )

    team_match = pd.DataFrame(team_records)

    team_match = team_match.merge(
        match_metadata[["p_match", "year"]],
        on="p_match",
        how="left",
        validate="many_to_one",
    )

    if team_match.duplicated(["p_match", "team"]).any():
        raise ValueError(
            "Team-match dataset contains duplicate "
            "(p_match, team) keys."
        )

    if team_match["p_match"].nunique() != match_summary["p_match"].nunique():
        raise ValueError(
            "Team-match dataset and match summary contain "
            "different numbers of matches."
        )

    return team_match