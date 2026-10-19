CREATE TABLE IF NOT EXISTS daily_weather (
                                             city             TEXT NOT NULL,
                                             date             DATE NOT NULL,
                                             temp_max_c       REAL,
                                             temp_min_c       REAL,
                                             precipitation_mm REAL,
                                             wind_max_kmh     REAL,
                                             loaded_at        TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (city, date)
    );