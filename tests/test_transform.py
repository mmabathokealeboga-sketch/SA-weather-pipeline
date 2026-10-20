import math

import pandas as pd

from src.transform import to_dataframe, clean


def make_df(**overrides):
    """One valid row; override any column to make it bad."""
    row = {
        "city": "Pretoria",
        "date": "2026-10-01",
        "temp_max_c": 25.0,
        "temp_min_c": 10.0,
        "precipitation_mm": 0.0,
        "wind_max_kmh": 12.0,
    }
    row.update(overrides)
    return pd.DataFrame([row])


def test_to_dataframe_renames_columns_and_adds_city():
    raw = {
        "city": "Durban",
        "daily": {
            "time": ["2026-10-01"],
            "temperature_2m_max": [24.0],
            "temperature_2m_min": [14.0],
            "precipitation_sum": [1.2],
            "wind_speed_10m_max": [20.0],
        },
    }
    df = to_dataframe(raw)
    assert list(df.columns) == [
        "city", "date", "temp_max_c", "temp_min_c", "precipitation_mm", "wind_max_kmh"
    ]
    assert df.iloc[0]["city"] == "Durban"


def test_valid_row_passes():
    good, rejected = clean(make_df())
    assert len(good) == 1
    assert len(rejected) == 0


def test_impossible_temperature_is_rejected():
    good, rejected = clean(make_df(temp_max_c=70.0))
    assert len(good) == 0
    assert len(rejected) == 1


def test_min_higher_than_max_is_rejected():
    good, rejected = clean(make_df(temp_min_c=30.0, temp_max_c=20.0))
    assert len(rejected) == 1


def test_negative_rain_is_rejected():
    good, rejected = clean(make_df(precipitation_mm=-1.0))
    assert len(rejected) == 1


def test_missing_value_is_rejected():
    good, rejected = clean(make_df(temp_max_c=math.nan))
    assert len(rejected) == 1


def test_duplicates_are_removed():
    df = pd.concat([make_df(), make_df()])
    good, rejected = clean(df)
    assert len(good) == 1
