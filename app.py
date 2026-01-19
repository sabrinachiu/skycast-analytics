import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(
    page_title="SkyCast Analytics",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Light Mode friendliness and aesthetics
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

def get_coordinates(city_name):
    """Fetch latitude and longitude for a given city name using Open-Meteo Geocoding API."""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            return result["latitude"], result["longitude"], result["name"], result.get("country", "")
    return None, None, None, None

def get_weather_data(lat, lon, start_date, end_date):
    """Fetch historical weather data from Open-Meteo Archive API."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "daily": "temperature_2m_max",
        "timezone": "auto"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "daily" in data:
            df = pd.DataFrame({
                "Date": pd.to_datetime(data["daily"]["time"]),
                "Max Temp": data["daily"]["temperature_2m_max"]
            })
            return df
    return None

# Header
st.title("🌤️ SkyCast Analytics")
st.markdown("### Historical Temperature Comparison Dashboard")
st.divider()

# Configuration Section
col1, col2 = st.columns(2)
with col1:
    city_a_input = st.text_input("City A", value="New York")
with col2:
    city_b_input = st.text_input("City B", value="London")

with st.sidebar:
    st.header("Settings")
    today = datetime.now()
    default_start = today - timedelta(days=30)
    date_range = st.date_input(
        "Select Date Range",
        value=(default_start, today),
        max_value=today
    )

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
    
    # Fetch Data
    with st.spinner("Fetching weather data..."):
        lat_a, lon_a, name_a, country_a = get_coordinates(city_a_input)
        lat_b, lon_b, name_b, country_b = get_coordinates(city_b_input)
        
        if lat_a and lat_b:
            df_a = get_weather_data(lat_a, lon_a, start_date, end_date)
            df_b = get_weather_data(lat_b, lon_b, start_date, end_date)
            
            if df_a is not None and df_b is not None:
                # Combine Data
                df_a["City"] = f"{name_a}, {country_a}"
                df_b["City"] = f"{name_b}, {country_b}"
                combined_df = pd.concat([df_a, df_b])
                
                # Metrics
                avg_a = df_a["Max Temp"].mean()
                avg_b = df_b["Max Temp"].mean()
                
                m1, m2 = st.columns(2)
                m1.metric(label=f"Avg Temp: {name_a}", value=f"{avg_a:.1f} °C")
                m2.metric(label=f"Avg Temp: {name_b}", value=f"{avg_b:.1f} °C")
                
                st.divider()

                # Tabs
                tab1, tab2 = st.tabs(["📈 Line Chart", "📋 Data Table"])
                
                with tab1:
                    st.subheader(f"Max Daily Temperature Comparison")
                    # Custom Blue: #b1cbf8, Custom Pink: #f1b7df
                    fig = px.line(
                        combined_df, 
                        x="Date", 
                        y="Max Temp", 
                        color="City",
                        labels={"Max Temp": "Max Temperature (°C)", "Date": "Date"},
                        template="plotly_white",
                        color_discrete_map={
                            f"{name_a}, {country_a}": "#b1cbf8", 
                            f"{name_b}, {country_b}": "#f1b7df"
                        }
                    )
                    fig.update_layout(
                        hovermode="x unified",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig, width="stretch")
                
                with tab2:
                    st.subheader("Raw Weather Data")
                    pivot_df = combined_df.pivot(index="Date", columns="City", values="Max Temp")
                    st.dataframe(pivot_df, width="stretch")
            else:
                st.error("Failed to fetch weather data. Please check the date range or try again later.")
        else:
            st.warning("Could not find one or both cities. Please check the spelling.")
else:
    st.info("Please select a valid date range (Start and End date).")
