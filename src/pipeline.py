import argparse
from datetime import date

from config.cities import CITIES
from src.extract import fetch_weather
from src.transform import to_dataframe, clean
from src.load import load


def run(start, end):
    """Extract, clean and load weather for every city between two dates."""
    for city, coords in CITIES.items():
        raw = fetch_weather(city, coords["lat"], coords["lon"], start.isoformat(), end.isoformat())
        good, rejected = clean(to_dataframe(raw))
        loaded = load(good) if not good.empty else 0
        print(f"{city}: {loaded} loaded, {len(rejected)} rejected")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SA weather pipeline")
    parser.add_argument("--start", type=date.fromisoformat, required=True)
    parser.add_argument("--end", type=date.fromisoformat, required=True)
    args = parser.parse_args()
    run(args.start, args.end)