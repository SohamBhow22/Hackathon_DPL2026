import pandas as pd


def audit_missingness(df: pd.DataFrame) -> pd.DataFrame:
    missingness = pd.DataFrame({
        "column": df.columns,
        "missing": df.isna().sum().values,
        "missing_pct": (df.isna().mean() * 100).values,
    })

    missingness = missingness.sort_values(
        by="missing",
        ascending=False
    ).reset_index(drop=True)

    return missingness

def audit_duplicates(df: pd.DataFrame) -> dict:
    results = {
        "duplicate_rows": df.duplicated().sum(),
        "duplicate_row_id": df["row_id"].duplicated().sum(),
        "duplicate_delivery_key": df[
            ["p_match", "inns", "ball_id"]
        ].duplicated().sum(),
    }

    return results

def audit_value_domains(df: pd.DataFrame) -> dict:
    results = {
        "innings_values": sorted(df["inns"].dropna().unique().tolist()),
        "year_values": sorted(df["year"].dropna().unique().tolist()),
        "competition_values": sorted(
            df["competition"].dropna().unique().tolist()
        ),
        "out_values": sorted(df["out"].dropna().unique().tolist()),
        "bat_out_values": sorted(
            df["bat_out"].dropna().unique().tolist()
        ),
        "noball_values": sorted(
            df["noball"].dropna().unique().tolist()
        ),
        "wide_values": sorted(
            df["wide"].dropna().unique().tolist()
        ),
        "byes_values": sorted(
            df["byes"].dropna().unique().tolist()
        ),
        "legbyes_values": sorted(
            df["legbyes"].dropna().unique().tolist()
        ),
        
    }

    return results

def audit_categorical_domains(df: pd.DataFrame) -> dict:
    """
    Return unique values for important categorical fields.
    """

    columns = [
        "team_bat",
        "team_bowl",
        "winner",
        "toss",
        "dismissal",
        "bat_hand",
        "bowl_style",
        "bowl_kind",
        "bowl_type",
        "shot",
        "line",
        "length",
    ]

    return {
        column: sorted(df[column].dropna().unique().tolist())
        for column in columns
    }