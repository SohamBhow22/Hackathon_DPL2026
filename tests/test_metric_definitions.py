import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from src.features.metric_definitions import (
    add_metric_features,
    derive_batting_dot,
    derive_bowler_credited_wicket,
    derive_bowling_dot,
    derive_legal_delivery,
    derive_match_phase,
)


@pytest.fixture
def sample_deliveries():
    """Small synthetic dataset covering normal and edge cases."""

    return pd.DataFrame(
        {
            "wide":     [0, 1, 0, 0, 0, 0, 0, 0, None, 0],
            "noball":   [0, 0, 1, 0, 0, 0, 0, 0, 0, None],
            "ballfaced": [1, 0, 1, 1, 1, 1, 1, 1, 1, 1],
            "batruns":  [0, 0, 0, 0, 4, 0, 0, 0, 0, 0],
            "score":    [0, 1, 1, 1, 4, 0, 1, 0, 0, 0],
            "out":      [False, False, False, True, False,
                         True, True, True, False, False],
            "dismissal": [
                None,
                None,
                None,
                "caught",
                None,
                "run out",
                "stumped",
                "retired not out (hurt)",
                None,
                None,
            ],
            "bowl": [
                "Bowler A",
                "Bowler B",
                "Bowler C",
                "Bowler D",
                "Bowler E",
                "Bowler F",
                "Bowler G",
                "Bowler H",
                "Bowler I",
                "Bowler J",
            ],
            "over_num": [1, 6, 7, 15, 16, 20, 1, 6, None, 21],
        }
    )


def test_legal_delivery_definition(sample_deliveries):
    result = derive_legal_delivery(sample_deliveries)

    expected = [
        True,   # Legal delivery
        False,  # Wide
        False,  # No-ball
        True,
        True,
        True,
        True,
        True,
        False,  # Missing wide value
        False,  # Missing no-ball value
    ]

    assert result.tolist() == expected


def test_batting_dot_definition(sample_deliveries):
    result = derive_batting_dot(sample_deliveries)

    expected = [
        True,   # Faced, zero batter runs
        False,  # Not counted as faced
        True,   # No-ball marked as faced, zero batter runs
        True,   # Zero batter runs on a dismissal
        False,  # Four runs off the bat
        True,   # Run out, zero batter runs
        True,   # Stumped, zero batter runs
        True,   # Retirement-related source record
        True,   # Missing wide value does not affect this definition
        True,
    ]

    assert result.tolist() == expected


def test_bowling_dot_requires_legal_delivery_and_zero_team_score(
    sample_deliveries,
):
    legal_delivery = derive_legal_delivery(sample_deliveries)

    result = derive_bowling_dot(
        sample_deliveries,
        legal_delivery=legal_delivery,
    )

    expected = [
        True,   # Legal delivery, zero team runs
        False,  # Wide
        False,  # No-ball
        False,  # Team scored one run
        False,  # Team scored four runs
        True,   # Legal delivery, zero team runs
        False,  # Leg-byes or other team runs: not a bowling dot
        True,   # Legal delivery, zero team runs
        False,  # Illegal under the missing-value handling
        False,
    ]

    assert result.tolist() == expected


def test_bowler_credited_wicket_definition(sample_deliveries):
    result = derive_bowler_credited_wicket(sample_deliveries)

    expected = [
        False,
        False,
        False,
        True,   # Caught
        False,
        False,  # Run out is not credited to the bowler
        True,   # Stumped
        False,  # Retirement-related dismissal label
        False,
        False,
    ]

    assert result.tolist() == expected


@pytest.mark.parametrize(
    ("over_num", "expected_phase"),
    [
        (1, "Powerplay"),
        (6, "Powerplay"),
        (7, "Middle"),
        (15, "Middle"),
        (16, "Death"),
        (20, "Death"),
        (None, pd.NA),
        (0, pd.NA),
        (21, pd.NA),
        (7.5, pd.NA),
        ("invalid", pd.NA),
    ],
)
def test_match_phase_boundaries(over_num, expected_phase):
    df = pd.DataFrame({"over_num": [over_num]})

    result = derive_match_phase(df)

    if pd.isna(expected_phase):
        assert pd.isna(result.iloc[0])
    else:
        assert result.iloc[0] == expected_phase


def test_legal_delivery_requires_columns():
    df = pd.DataFrame({"wide": [0]})

    with pytest.raises(ValueError, match="Missing columns"):
        derive_legal_delivery(df)


def test_batting_dot_requires_columns():
    df = pd.DataFrame({"ballfaced": [1]})

    with pytest.raises(ValueError, match="Missing columns"):
        derive_batting_dot(df)


def test_bowling_dot_requires_score():
    df = pd.DataFrame(
        {
            "wide": [0],
            "noball": [0],
        }
    )

    with pytest.raises(ValueError, match="score"):
        derive_bowling_dot(df)


def test_bowler_credited_wicket_requires_columns():
    df = pd.DataFrame({"out": [True]})

    with pytest.raises(ValueError, match="Missing columns"):
        derive_bowler_credited_wicket(df)


def test_supplied_legal_delivery_index_must_match():
    df = pd.DataFrame(
        {
            "wide": [0, 0],
            "noball": [0, 0],
            "score": [0, 1],
        },
        index=[10, 20],
    )

    legal_delivery = pd.Series(
        [True, True],
        index=[0, 1],
    )

    with pytest.raises(ValueError, match="index must match"):
        derive_bowling_dot(
            df,
            legal_delivery=legal_delivery,
        )


def test_add_metric_features_does_not_mutate_input(sample_deliveries):
    original = sample_deliveries.copy(deep=True)

    result = add_metric_features(sample_deliveries)

    # The input DataFrame must remain unchanged.
    assert_frame_equal(sample_deliveries, original)

    # The result must be a separate DataFrame.
    assert result is not sample_deliveries

    expected_columns = {
        "legal_delivery",
        "batting_dot",
        "bowling_dot",
        "bowler_credited_wicket",
        "match_phase",
    }

    assert expected_columns.issubset(result.columns)

    # Original columns and values must remain present in the result.
    assert_frame_equal(
        result[original.columns],
        original,
    )