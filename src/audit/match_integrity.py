import pandas as pd


def audit_match_metadata_consistency(df: pd.DataFrame) -> pd.DataFrame:
    metadata_columns = [
        "year",
        "match_date",
        "ground",
        "country",
        "winner",
        "toss",
        "competition",
    ]

    consistency = (
        df.groupby("p_match")[metadata_columns]
        .nunique(dropna=False)
        .reset_index()
    )

    return consistency

def audit_match_innings_structure(df: pd.DataFrame) -> pd.DataFrame:
    innings_summary = (
        df.groupby(["p_match", "inns"])
        .agg(
            deliveries=("ball_id", "count"),
            max_balls=("max_balls", "first"),
            inns_balls=("inns_balls", "max"),
        )
        .reset_index()
    )

    match_summary = (
        innings_summary.groupby("p_match")
        .agg(
            innings_count=("inns", "nunique"),
            total_deliveries=("deliveries", "sum"),
            max_balls_in_match=("max_balls", "max"),
        )
        .reset_index()
    )

    return match_summary

def audit_innings_length(df: pd.DataFrame) -> pd.DataFrame:
    innings_length = (
        df.groupby(["p_match", "inns"])
        .agg(
            max_balls=("max_balls", "first"),
            actual_deliveries=("ball_id", "count"),
        )
        .reset_index()
    )

    return innings_length

def audit_match_results(df: pd.DataFrame) -> pd.DataFrame:
    match_results = (
        df.groupby("p_match")
        .agg(
            winner=("winner", "first"),
            innings_count=("inns", "nunique"),
            teams=("team_bat", lambda x: sorted(x.dropna().unique().tolist())),
        )
        .reset_index()
    )

    match_results["winner_in_teams"] = match_results.apply(
        lambda row: (
            row["winner"] == "-"
            or row["winner"] in row["teams"]
        ),
        axis=1,
    )

    match_results["complete_two_innings"] = (
        match_results["innings_count"] == 2
    )

    return match_results