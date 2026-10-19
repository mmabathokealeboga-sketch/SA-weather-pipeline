import argparse
from datetime import date, timedelta

from config.cities import CITIES
from src.extract import fetch_weather
from src.transform import to_dataframe, clean
from src.load import load, get_last_date

DEFAULT_START = date(2023, 1, 1)
API_LAG_DAYS = 5


def run_city(city, coords, start, end):
    if start > end:
        print(f"{city}: already up to date")
        return
    raw = fetch_weather(city, coords["lat"], coords["lon"], start.isoformat(), end.isoformat())
    good, rejected = clean(to_dataframe(raw))
    loaded = load(good) if not good.empty else 0
    print(f"{city}: {start} to {end} -> {loaded} loaded, {len(rejected)} rejected")


def run(start=None, end=None):
    """No --start given = incremental: carry on from each city's last stored date."""
    end = end or date.today() - timedelta(days=API_LAG_DAYS)
    for city, coords in CITIES.items():
        if start:
            city_start = start
        else:
            last = get_last_date(city)
            city_start = last + timedelta(days=1) if last else DEFAULT_START
        run_city(city, coords, city_start, end)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SA weather pipeline")
    parser.add_argument("--start", type=date.fromisoformat, help="backfill from this date")
    parser.add_argument("--end", type=date.fromisoformat, help="defaults to 5 days ago")
    args = parser.parse_args()
    run(args.start, args.end)