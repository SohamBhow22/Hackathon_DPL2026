import pandas as pd


def audit_team_coverage(
    df: pd.DataFrame,
    team: str = "Kolkata Knight Riders"
) -> pd.DataFrame:

    team_matches = (
        df[
            (df["team_bat"] == team) |
            (df["team_bowl"] == team)
        ]
        .groupby("p_match")
        .agg(
            year=("year", "first"),
            match_date=("match_date", "first"),
            ground=("ground", "first"),
            winner=("winner", "first"),
            innings_count=("inns", "nunique"),
            opponents=("team_bat", lambda x: sorted(
                [t for t in x.unique() if t != team]
            )),
        )
        .reset_index()
    )

    team_matches["complete_two_innings"] = (
        team_matches["innings_count"] == 2
    )

    return team_matches