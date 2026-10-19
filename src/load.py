import os

import psycopg2
from psycopg2.extras import execute_values


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5433"),
        dbname=os.getenv("DB_NAME", "weather"),
        user=os.getenv("DB_USER", "weather"),
        password=os.getenv("DB_PASSWORD", "weather"),
    )


def load(df):
    """Insert rows. If a city+date already exists, update it instead of duplicating."""
    rows = list(df.itertuples(index=False, name=None))
    sql = """
        INSERT INTO daily_weather
            (city, date, temp_max_c, temp_min_c, precipitation_mm, wind_max_kmh)
        VALUES %s
        ON CONFLICT (city, date) DO UPDATE SET
            temp_max_c = EXCLUDED.temp_max_c,
            temp_min_c = EXCLUDED.temp_min_c,
            precipitation_mm = EXCLUDED.precipitation_mm,
            wind_max_kmh = EXCLUDED.wind_max_kmh,
            loaded_at = NOW()
    """
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            execute_values(cur, sql, rows)
    finally:
        conn.close()
    return len(rows)