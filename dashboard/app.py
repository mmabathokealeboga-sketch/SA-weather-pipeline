import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st

# Let the dashboard import from src/ no matter where it is launched from
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.load import get_connection  # noqa: E402

st.set_page_config(page_title="SA Weather Dashboard", page_icon="🌦️", layout="wide")


@st.cache_data(ttl=300)
def load_data():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT city, date, temp_max_c, temp_min_c, precipitation_mm, wind_max_kmh "
                "FROM daily_weather ORDER BY date"
            )
            columns = [col[0] for col in cur.description]
            rows = cur.fetchall()
    finally:
        conn.close()
    df = pd.DataFrame(rows, columns=columns)
    df["date"] = pd.to_datetime(df["date"])
    return df


st.title("🌦️ South African Weather Dashboard")

try:
    data = load_data()
except psycopg2.OperationalError:
    st.error("Can't reach the database. Start it with: docker compose up -d db")
    st.stop()

if data.empty:
    st.warning("No data yet. Run the pipeline first.")
    st.stop()


st.sidebar.header("Filters")
city = st.sidebar.selectbox("City", sorted(data["city"].unique()))
min_date, max_date = data["date"].min().date(), data["date"].max().date()
picked = st.sidebar.date_input(
    "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
)
start, end = picked if len(picked) == 2 else (min_date, max_date)

in_range = data[(data["date"].dt.date >= start) & (data["date"].dt.date <= end)]
city_df = in_range[in_range["city"] == city]


st.subheader(f"{city}: {start} to {end}")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Avg max temp", f"{city_df['temp_max_c'].mean():.1f} °C")
c2.metric("Avg min temp", f"{city_df['temp_min_c'].mean():.1f} °C")
c3.metric("Total rain", f"{city_df['precipitation_mm'].sum():.1f} mm")
c4.metric("Top wind", f"{city_df['wind_max_kmh'].max():.1f} km/h")


temp_long = city_df.melt(
    id_vars="date",
    value_vars=["temp_max_c", "temp_min_c"],
    var_name="type",
    value_name="°C",
)
temp_long["type"] = temp_long["type"].map({"temp_max_c": "Max", "temp_min_c": "Min"})
st.plotly_chart(
    px.line(temp_long, x="date", y="°C", color="type", title="Temperature"),
    width="stretch",
)
st.plotly_chart(
    px.bar(city_df, x="date", y="precipitation_mm", title="Rainfall (mm)"),
    width="stretch",
)


st.subheader("All cities compared")
summary = (
    in_range.groupby("city")
    .agg(
        avg_max_c=("temp_max_c", "mean"),
        avg_min_c=("temp_min_c", "mean"),
        total_rain_mm=("precipitation_mm", "sum"),
        top_wind_kmh=("wind_max_kmh", "max"),
    )
    .round(1)
    .reset_index()
)
st.dataframe(summary, width="stretch", hide_index=True)