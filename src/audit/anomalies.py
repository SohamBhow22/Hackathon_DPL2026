import pandas as pd


RCB_NAMES = {
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
    "Royal Challengers Bengaluru": "Royal Challengers Bengaluru",
}


def audit_team_name_consistency(df: pd.DataFrame) -> dict:
    """Audit team-name variants that may represent the same franchise."""

    team_values = set(
        pd.concat(
            [
                df["team_bat"],
                df["team_bowl"],
                df["winner"],
                df["toss"],
            ]
        )
        .dropna()
        .unique()
    )

    rcb_variants = sorted(
        team_values.intersection(RCB_NAMES.keys())
    )

    return {
        "rcb_variants_found": rcb_variants,
        "variant_count": len(rcb_variants),
        "normalization_required": len(rcb_variants) > 1,
    }


def audit_innings_length_anomalies(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Audit unusual max_balls values and observed delivery counts."""

    result = (
        df.groupby(["p_match", "inns"])
        .agg(
            max_balls=("max_balls", "first"),
            delivery_count=("ball_id", "nunique"),
            match_date=("match_date", "first"),
            year=("year", "first"),
        )
        .reset_index()
    )

    result["max_balls_zero"] = result["max_balls"] == 0

    result["reduced_length"] = (
        (result["max_balls"] > 0)
        & (result["max_balls"] < 120)
    )

    return result


def audit_score_extras_reconciliation(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Identify rows where the naive score/extras equation does not hold."""

    calculated_score = (
        df["batruns"]
        + df["wide"]
        + df["noball"]
        + df["byes"]
        + df["legbyes"]
    )

    anomalies = df.loc[
        df["score"] != calculated_score
    ].copy()

    anomalies["calculated_score"] = calculated_score.loc[
        anomalies.index
    ]

    return anomalies[
        [
            "p_match",
            "inns",
            "ball_id",
            "score",
            "batruns",
            "wide",
            "noball",
            "byes",
            "legbyes",
            "calculated_score",
            "outcome",
        ]
    ]


def audit_wicket_semantics(
    df: pd.DataFrame,
) -> dict:
    """Audit relationships between wicket-event and dismissal fields."""

    wicket_rows = df[df["out"] == True]

    return {
        "wicket_events": len(wicket_rows),
        "missing_dismissal": int(
            wicket_rows["dismissal"].isna().sum()
        ),
        "missing_p_out": int(
            wicket_rows["p_out"].isna().sum()
        ),
        "bat_out_false": int(
            (wicket_rows["bat_out"] == False).sum()
        ),
    }


def audit_tactical_missingness(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Summarise missingness in tactical/tracking variables."""

    tactical_columns = [
        "bowl_speed_category",
        "bowl_release_point",
        "bowl_type",
        "control",
        "shot",
        "line",
        "length",
    ]

    result = pd.DataFrame(
        {
            "column": tactical_columns,
            "missing": [
                df[column].isna().sum()
                for column in tactical_columns
            ],
            "missing_pct": [
                df[column].isna().mean() * 100
                for column in tactical_columns
            ],
        }
    )

    return result


def audit_delivery_key(
    df: pd.DataFrame,
) -> dict:
    """Validate the analytical delivery key."""

    key_columns = [
        "p_match",
        "inns",
        "ball_id",
    ]

    duplicate_count = df.duplicated(
        subset=key_columns
    ).sum()

    return {
        "key_columns": key_columns,
        "duplicate_key_rows": int(duplicate_count),
        "unique_key": bool(duplicate_count == 0),
    }


def audit_incomplete_matches(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Identify matches that do not contain two innings."""

    result = (
        df.groupby("p_match")
        .agg(
            innings_count=("inns", "nunique"),
            winner=("winner", "first"),
            year=("year", "first"),
            match_date=("match_date", "first"),
        )
        .reset_index()
    )

    return result[
        result["innings_count"] != 2
    ].copy()


def audit_schema_naming() -> pd.DataFrame:
    """Document known Data Dictionary vs CSV naming differences."""

    return pd.DataFrame(
        {
            "data_dictionary_name": [
                "over",
                "date",
                "wagonX",
                "wagonY",
                "wagonZone",
            ],
            "csv_name": [
                "over_num",
                "match_date",
                "wagonx",
                "wagony",
                "wagonzone",
            ],
        }
    )


def normalize_team_name(team: str) -> str:
    """Return the analytical team name for a raw team label."""

    return RCB_NAMES.get(team, team)


def audit_delivery_order(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Identify matches where physical CSV row order
    differs from natural innings order.
    """

    physical_order = (
        df.groupby("p_match")["inns"]
        .apply(lambda x: list(pd.unique(x)))
        .reset_index(
            name="physical_innings_order"
        )
    )

    physical_order["expected_innings_order"] = (
        physical_order["physical_innings_order"]
        .apply(sorted)
    )

    physical_order["order_mismatch"] = (
        physical_order["physical_innings_order"]
        != physical_order["expected_innings_order"]
    )

    return physical_order[
        physical_order["order_mismatch"]
    ].copy()