from datetime import date
from unittest.mock import MagicMock, patch

import pandas as pd

from src.load import get_connection, get_last_date, load


def make_df(rows=2):
    return pd.DataFrame(
        [
            {
                "city": "Pretoria",
                "date": f"2026-10-0{i + 1}",
                "temp_max_c": 25.0,
                "temp_min_c": 10.0,
                "precipitation_mm": 0.0,
                "wind_max_kmh": 12.0,
            }
            for i in range(rows)
        ]
    )


@patch("src.load.psycopg2.connect")
def test_get_connection_uses_defaults(mock_connect, monkeypatch):
    for name in ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]:
        monkeypatch.delenv(name, raising=False)

    get_connection()

    mock_connect.assert_called_once_with(
        host="localhost", port="5433", dbname="weather", user="weather", password="weather"
    )


@patch("src.load.psycopg2.connect")
def test_get_connection_reads_environment(mock_connect, monkeypatch):
    monkeypatch.setenv("DB_HOST", "db")
    monkeypatch.setenv("DB_PORT", "5432")

    get_connection()

    kwargs = mock_connect.call_args.kwargs
    assert kwargs["host"] == "db"
    assert kwargs["port"] == "5432"


@patch("src.load.execute_values")
@patch("src.load.get_connection")
def test_load_returns_number_of_rows(mock_get_conn, mock_execute_values):
    mock_get_conn.return_value = MagicMock()

    assert load(make_df(rows=2)) == 2


@patch("src.load.execute_values")
@patch("src.load.get_connection")
def test_load_sends_rows_with_upsert_sql(mock_get_conn, mock_execute_values):
    mock_get_conn.return_value = MagicMock()

    load(make_df(rows=2))

    args = mock_execute_values.call_args.args
    sql, rows = args[1], args[2]
    assert "ON CONFLICT (city, date) DO UPDATE" in sql
    assert len(rows) == 2
    assert rows[0][0] == "Pretoria"


@patch("src.load.execute_values")
@patch("src.load.get_connection")
def test_load_closes_connection(mock_get_conn, mock_execute_values):
    conn = MagicMock()
    mock_get_conn.return_value = conn

    load(make_df())

    conn.close.assert_called_once()


@patch("src.load.get_connection")
def test_get_last_date_returns_date(mock_get_conn):
    conn = MagicMock()
    cur = conn.cursor.return_value.__enter__.return_value
    cur.fetchone.return_value = (date(2026, 10, 21),)
    mock_get_conn.return_value = conn

    assert get_last_date("Pretoria") == date(2026, 10, 21)
    conn.close.assert_called_once()


@patch("src.load.get_connection")
def test_get_last_date_returns_none_when_no_data(mock_get_conn):
    conn = MagicMock()
    cur = conn.cursor.return_value.__enter__.return_value
    cur.fetchone.return_value = (None,)
    mock_get_conn.return_value = conn

    assert get_last_date("Durban") is None