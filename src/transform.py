import pandas as pd

COLUMN_NAMES = {
    "time": "date",
    "temperature_2m_max": "temp_max_c",
    "temperature_2m_min": "temp_min_c",
    "precipitation_sum": "precipitation_mm",
    "wind_speed_10m_max": "wind_max_kmh",
}


def to_dataframe(raw):
    """Turn raw API data into a table: one row per city per day."""
    df = pd.DataFrame(raw["daily"])
    df = df.rename(columns=COLUMN_NAMES)
    df["city"] = raw["city"]
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df[["city", "date", "temp_max_c", "temp_min_c", "precipitation_mm", "wind_max_kmh"]]


def clean(df):
    """Remove duplicates and impossible readings. Returns (good_rows, rejected_rows)."""
    df = df.drop_duplicates(subset=["city", "date"])

    valid = (
        df["temp_max_c"].between(-15, 50)
        & df["temp_min_c"].between(-15, 50)
        & (df["temp_min_c"] <= df["temp_max_c"])
        & (df["precipitation_mm"] >= 0)
        & df["wind_max_kmh"].between(0, 200)
    )

    good = df[valid].reset_index(drop=True)
    rejected = df[~valid].reset_index(drop=True)
    return good, rejected