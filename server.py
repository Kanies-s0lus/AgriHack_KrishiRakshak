import os
import asyncpg
import httpx
import joblib
import anyio
from fastmcp import FastMCP, Context
from dotenv import load_dotenv


# Initialize FastMCP server
mcp = FastMCP(name="CropDiseasePredictor")

# Configuration from environment (database and API keys)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "mydatabase")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "PLACEHOLDER")


async def fetch_weather(lat: float, lon: float) -> dict:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    temp = data.get("main", {}).get("temp")
    humidity = data.get("main", {}).get("humidity")
    return {"temperature": temp, "humidity": humidity}

@mcp.tool()
async def get_weather(lat: float, lon: float) -> dict:
    return await fetch_weather(lat, lon)

import joblib
import pandas as pd

# Load the model once (on server start)
try:
    disease_model = joblib.load("crop_disease_model.pkl")
    print("✅ Model loaded successfully")
except Exception as e:
    print("⚠️ Failed to load model:", e)
    disease_model = None

@mcp.tool
async def get_crop_points(
    crop_name: str,
    age_days: int,
    soil_type: str,
    lat: float,
    lon: float,
    rainfall_mm: float = 0.0,
    growth_stage: str = "Default",
    ctx: Context = None
) -> str:
    """
    Returns a dynamic "points" string for a crop card.
    Combines weather info and predicted disease.
    """
    # Fetch weather dynamically
    weather = await fetch_weather(lat, lon)
    temp_c = weather.get("temperature", 30.0)
    humidity_pct = weather.get("humidity", 70.0)

    if not disease_model:
        return "🚫 Model not loaded. Please check your 'crop_disease_model.pkl'."

    # Prepare input for prediction
    input_df = pd.DataFrame([{
        "Crop": crop_name,
        "AgeDays": age_days,
        "TempC": temp_c,
        "HumidityPct": humidity_pct,
        "RainfallMm": rainfall_mm,
        "SoilType": soil_type,
        "GrowthStage": growth_stage
    }])

    try:
        prediction = disease_model.predict(input_df)[0]
        return f"🌾 Predicted Disease: {prediction}\n☀️ Temp: {temp_c}°C, 💧 Humidity: {humidity_pct}%"
    except Exception as e:
        return f"⚠️ Prediction failed: {str(e)}"
    
if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)