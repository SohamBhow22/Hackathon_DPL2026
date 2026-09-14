import pandas as pd

from src.audit.anomalies import (
    audit_team_name_consistency,
    audit_innings_length_anomalies,
    audit_score_extras_reconciliation,
    audit_wicket_semantics,
    audit_tactical_missingness,
    audit_delivery_key,
    audit_incomplete_matches,
    audit_delivery_order,
    audit_schema_naming,
    normalize_team_name,
)


def test_delivery_key_is_unique():
    df = pd.DataFrame(
        {
            "p_match": [1, 1, 1],
            "inns": [1, 1, 2],
            "ball_id": [1, 2, 1],
        }
    )

    result = audit_delivery_key(df)

    assert result["duplicate_key_rows"] == 0
    assert result["unique_key"] is True


def test_delivery_key_detects_duplicates():
    df = pd.DataFrame(
        {
            "p_match": [1, 1, 1],
            "inns": [1, 1, 1],
            "ball_id": [1, 1, 2],
        }
    )

    result = audit_delivery_key(df)

    assert result["duplicate_key_rows"] == 1
    assert result["unique_key"] is False


def test_rcb_names_are_normalized():
    assert (
        normalize_team_name(
            "Royal Challengers Bangalore"
        )
        == "Royal Challengers Bengaluru"
    )

    assert (
        normalize_team_name(
            "Royal Challengers Bengaluru"
        )
        == "Royal Challengers Bengaluru"
    )


def test_team_name_audit_detects_rcb_variants():
    df = pd.DataFrame(
        {
            "team_bat": [
                "Royal Challengers Bangalore",
                "Royal Challengers Bengaluru",
            ],
            "team_bowl": [
                "Kolkata Knight Riders",
                "Kolkata Knight Riders",
            ],
            "winner": [
                "Royal Challengers Bangalore",
                "Royal Challengers Bengaluru",
            ],
            "toss": [
                "Royal Challengers Bangalore",
                "Royal Challengers Bengaluru",
            ],
        }
    )

    result = audit_team_name_consistency(df)

    assert result["variant_count"] == 2
    assert result["normalization_required"] is True


def test_wicket_semantics_require_dismissal_and_player():
    df = pd.DataFrame(
        {
            "out": [True, False, True],
            "dismissal": [
                "bowled",
                None,
                "run out",
            ],
            "p_out": [
                "Player A",
                None,
                "Player B",
            ],
            "bat_out": [
                True,
                False,
                False,
            ],
        }
    )

    result = audit_wicket_semantics(df)

    assert result["wicket_events"] == 2
    assert result["missing_dismissal"] == 0
    assert result["missing_p_out"] == 0


def test_incomplete_matches_are_detected():
    df = pd.DataFrame(
        {
            "p_match": [1, 1, 2],
            "inns": [1, 2, 1],
            "winner": [
                "Team A",
                "Team A",
                "-",
            ],
            "year": [
                2024,
                2024,
                2023,
            ],
            "match_date": [
                "2024-01-01",
                "2024-01-01",
                "2023-01-01",
            ],
        }
    )

    result = audit_incomplete_matches(df)

    assert len(result) == 1
    assert result.iloc[0]["p_match"] == 2


def test_reduced_length_innings_are_not_zero_length():
    df = pd.DataFrame(
        {
            "p_match": [1, 1, 2],
            "inns": [1, 2, 1],
            "max_balls": [120, 96, 90],
            "ball_id": [1, 1, 1],
            "match_date": [
                "2024-01-01",
                "2024-01-01",
                "2024-01-01",
            ],
            "year": [
                2024,
                2024,
                2024,
            ],
        }
    )

    result = audit_innings_length_anomalies(df)

    reduced = result[
        result["reduced_length"]
    ]

    assert len(reduced) == 2
    assert reduced["max_balls_zero"].sum() == 0


def test_delivery_order_audit_detects_physical_order_issue():
    df = pd.DataFrame(
        {
            "p_match": [1, 1, 2, 2],
            "inns": [1, 1, 2, 1],
        }
    )

    result = audit_delivery_order(df)

    assert len(result) == 1
    assert result.iloc[0]["p_match"] == 2


def test_schema_naming_mapping_exists():
    result = audit_schema_naming()

    assert len(result) == 5

    assert "data_dictionary_name" in result.columns
    assert "csv_name" in result.columns

    mapping = dict(
        zip(
            result["data_dictionary_name"],
            result["csv_name"],
        )
    )

    assert mapping["over"] == "over_num"
    assert mapping["date"] == "match_date"
    assert mapping["wagonX"] == "wagonx"
    assert mapping["wagonY"] == "wagony"
    assert mapping["wagonZone"] == "wagonzone"