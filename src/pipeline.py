import argparse
import logging
from datetime import date, timedelta
from pathlib import Path

from config.cities import CITIES
from src.extract import fetch_weather
from src.transform import to_dataframe, clean
from src.load import load, get_last_date

DEFAULT_START = date(2023, 1, 1)
API_LAG_DAYS = 5  # the archive API is a few days behind today

log = logging.getLogger("pipeline")


def setup_logging():
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler("logs/pipeline.log"),
            logging.StreamHandler(),
        ],
    )


def run_city(city, coords, start, end):
    if start > end:
        log.info("%s: already up to date", city)
        return
    raw = fetch_weather(city, coords["lat"], coords["lon"], start.isoformat(), end.isoformat())
    good, rejected = clean(to_dataframe(raw))
    loaded = load(good) if not good.empty else 0
    log.info("%s: %s to %s -> %d loaded, %d rejected", city, start, end, loaded, len(rejected))
    for _, row in rejected.iterrows():
        log.warning("%s: rejected row for %s: %s", city, row["date"], row.to_dict())


def run(start=None, end=None):
    """No --start given = incremental: carry on from each city's last stored date."""
    end = end or date.today() - timedelta(days=API_LAG_DAYS)
    log.info("Pipeline started (end date %s)", end)
    failed = []
    for city, coords in CITIES.items():
        try:
            if start:
                city_start = start
            else:
                last = get_last_date(city)
                city_start = last + timedelta(days=1) if last else DEFAULT_START
            run_city(city, coords, city_start, end)
        except Exception:
            log.exception("%s: failed", city)
            failed.append(city)
    log.info("Pipeline finished. Failed cities: %s", failed or "none")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SA weather pipeline")
    parser.add_argument("--start", type=date.fromisoformat, help="backfill from this date")
    parser.add_argument("--end", type=date.fromisoformat, help="defaults to 5 days ago")
    args = parser.parse_args()
    setup_logging()
    run(args.start, args.end)