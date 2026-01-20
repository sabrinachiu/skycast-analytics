import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(
    page_title="SkyCast Analytics",
    page_icon="🌤️",
    layout="wide"
)

@st.cache_data(ttl=3600)
def get_coordinates(city_name):
    """Fetch latitude and longitude for a given city name."""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                result = data["results"][0]
                return result["latitude"], result["longitude"], result["name"], result.get("country", "")
    except Exception:
        pass
    return None, None, None, None

@st.cache_data(ttl=3600)
def get_weather_data(lat, lon, start_date, end_date):
    """Fetch historical weather data."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "daily": "temperature_2m_max",
        "timezone": "auto"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "daily" in data:
                df = pd.DataFrame({
                    "Date": pd.to_datetime(data["daily"]["time"]),
                    "Max Temp": data["daily"]["temperature_2m_max"]
                })
                return df
    except Exception:
        pass
    return None

# Header
st.title("🌤️ SkyCast Analytics")
st.markdown("Historical Temperature Comparison Dashboard")

# Sidebar Configuration
with st.sidebar:
    st.header("Settings")
    city_a_input = st.text_input("City A", value="New York")
    city_b_input = st.text_input("City B", value="London")
    
    today = datetime.now().date()
    default_start = today - timedelta(days=30)
    date_range = st.date_input(
        "Select Date Range",
        value=(default_start, today),
        max_value=today
    )

# Main Logic
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
    
    with st.spinner("Fetching data..."):
        lat_a, lon_a, name_a, country_a = get_coordinates(city_a_input)
        lat_b, lon_b, name_b, country_b = get_coordinates(city_b_input)
        
        if lat_a and lat_b:
            df_a = get_weather_data(lat_a, lon_a, start_date, end_date)
            df_b = get_weather_data(lat_b, lon_b, start_date, end_date)
            
            if df_a is not None and df_b is not None:
                # Metrics
                avg_a = df_a["Max Temp"].mean()
                avg_b = df_b["Max Temp"].mean()
                
                m1, m2 = st.columns(2)
                m1.metric(f"Avg Temp: {name_a}", f"{avg_a:.1f} °C")
                m2.metric(f"Avg Temp: {name_b}", f"{avg_b:.1f} °C")
                
                # Data Processing
                df_a["City"] = f"{name_a}, {country_a}"
                df_b["City"] = f"{name_b}, {country_b}"
                combined_df = pd.concat([df_a, df_b])
                
                # Tabs
                tab1, tab2 = st.tabs(["📈 Chart", "📋 Table"])
                
                with tab1:
                    fig = px.line(
                        combined_df, 
                        x="Date", 
                        y="Max Temp", 
                        color="City",
                        template="plotly_white",
                        color_discrete_map={
                            f"{name_a}, {country_a}": "#b1cbf8", 
                            f"{name_b}, {country_b}": "#f1b7df"
                        }
                    )
                    fig.update_layout(hovermode="x unified")
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    pivot_df = combined_df.pivot(index="Date", columns="City", values="Max Temp")
                    st.dataframe(pivot_df, use_container_width=True)
            else:
                st.error("Weather data not found for these dates.")
        else:
            st.warning("One or both cities not found.")
else:
    st.info("Please select a start and end date in the sidebar.")
