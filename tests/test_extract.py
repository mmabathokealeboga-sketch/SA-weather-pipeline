from unittest.mock import MagicMock, patch

import pytest
import requests

from src.extract import ARCHIVE_URL, DAILY_FIELDS, fetch_weather


def fake_response(json_data):
    """A pretend API response, so tests never touch the internet."""
    response = MagicMock()
    response.json.return_value = json_data
    return response


@patch("src.extract.requests.get")
def test_fetch_weather_adds_city_to_result(mock_get):
    mock_get.return_value = fake_response({"daily": {"time": []}})

    result = fetch_weather("Durban", -29.8587, 31.0218, "2026-10-01", "2026-10-05")

    assert result["city"] == "Durban"
    assert "daily" in result


@patch("src.extract.requests.get")
def test_fetch_weather_sends_correct_request(mock_get):
    mock_get.return_value = fake_response({})

    fetch_weather("Pretoria", -25.7479, 28.2293, "2026-10-01", "2026-10-05")

    args, kwargs = mock_get.call_args
    assert args[0] == ARCHIVE_URL
    assert kwargs["params"]["latitude"] == -25.7479
    assert kwargs["params"]["longitude"] == 28.2293
    assert kwargs["params"]["start_date"] == "2026-10-01"
    assert kwargs["params"]["end_date"] == "2026-10-05"
    assert kwargs["params"]["daily"] == ",".join(DAILY_FIELDS)
    assert kwargs["timeout"] == 30


@patch("src.extract.requests.get")
def test_fetch_weather_raises_on_http_error(mock_get):
    response = fake_response({})
    response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
    mock_get.return_value = response

    with pytest.raises(requests.HTTPError):
        fetch_weather("Cape Town", -33.9249, 18.4241, "2026-10-01", "2026-10-05")