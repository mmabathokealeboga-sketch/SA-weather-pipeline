# SA Weather Pipeline

An automated ETL pipeline that collects daily weather data for 8 South African cities, validates it, and loads it into a PostgreSQL database.

> 🚧 Work in progress: dashboard, tests and scheduling coming soon.

## What it does

1. **Extract**: pulls daily weather from the [Open-Meteo](https://open-meteo.com/) archive API
2. **Transform**: converts raw API data into a clean table (one row per city per day)
3. **Validate**: rejects impossible readings (e.g. temperatures above 50°C, min higher than max)
4. **Load**: upserts into PostgreSQL, so re-running never creates duplicate rows

The pipeline supports:
- **Backfill**: load historical data for any date range
- **Incremental loads**: each run only fetches days that aren't in the database yet

## Cities tracked

Johannesburg, Pretoria, Cape Town, Durban, Gqeberha, Bloemfontein, Polokwane, Mbombela

## Data collected

| Column | Description |
|---|---|
| `city` | City name |
| `date` | Day of the reading |
| `temp_max_c` | Maximum temperature (°C) |
| `temp_min_c` | Minimum temperature (°C) |
| `precipitation_mm` | Total rainfall (mm) |
| `wind_max_kmh` | Maximum wind speed (km/h) |

## Tech stack

Python · pandas · PostgreSQL · Docker Compose · psycopg2

## Project structure

```
├── config/cities.py     # cities and their coordinates
├── src/
│   ├── extract.py       # fetch data from the API
│   ├── transform.py     # clean and validate
│   ├── load.py          # write to PostgreSQL
│   └── pipeline.py      # runs the full pipeline
├── db/schema.sql        # database table definition
└── docker-compose.yml   # PostgreSQL container
```

## Getting started

**Requirements:** Python 3.10+, Docker

```bash
# 1. Clone and set up
git clone https://github.com/mmabathokealeboga-sketch/SA-weather-pipeline.git
cd SA-weather-pipeline
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Start the database
docker compose up -d

# 3. Backfill historical data
python3 -m src.pipeline --start 2023-01-01 --end 2026-10-10

# 4. Run incrementally (only fetches new days)
python3 -m src.pipeline
```

## Roadmap

- [x] Extract, transform, validate, load
- [x] Historical backfill
- [x] Incremental loads
- [ ] Logging
- [ ] Unit tests
- [ ] Containerise the pipeline
- [ ] Streamlit dashboard
- [ ] Daily scheduling# SA-weather-pipeline