import os, requests
from statistics import mean
from dotenv import load_dotenv

# --- CONST ---
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_LOCATION = os.getenv("WEATHER_LOCATION")

def get_weather_summary():
    try:
        url = (
            "https://api.weatherapi.com/v1/forecast.json"
            f"?key={WEATHER_API_KEY}"
            f"&q={WEATHER_LOCATION}"
            f"&days=1&aqi=no&alerts=no"
        )
        resp = requests.get(url, timeout=5).json()

        cur = resp["current"]
        fc = resp["forecast"]["forecastday"][0]["day"]
        ast = resp["forecast"]["forecastday"][0]["astro"]
        hours = resp["forecast"]["forecastday"][0]["hour"]

        # Basic conditions
        cond = cur["condition"]["text"]
        temp_c = int(cur["temp_c"])
        feelslike_c = int(cur["feelslike_c"])
        high_c = int(fc["maxtemp_c"])
        low_c  = int(fc["mintemp_c"])
        sunset_time = ast.get("sunset")

        # Hour range
        start_hour = 8
        end_hour = 23

        # Helper to extract hour from "2025-11-26 03:00"
        def extract_hour(h):
            return int(h["time"].split(" ")[1].split(":")[0])

        # Get average rain chance
        rain_vals = [h["chance_of_rain"] for h in hours
                     if start_hour <= extract_hour(h) <= end_hour]
        avg_rain_chance = mean(rain_vals) if rain_vals else 0
        print(f"avg_rain_chance: {avg_rain_chance}")

        # Get average snow chance
        snow_vals = [h["chance_of_snow"] for h in hours
                     if start_hour <= extract_hour(h) <= end_hour]
        avg_snow_chance = mean(snow_vals) if snow_vals else 0
        print(f"avg_snow_chance: {avg_snow_chance}")

        # Build summary
        pieces = [
            cond,
            f"Current: {temp_c}°C | Feels: {feelslike_c}°C",
            f"H {high_c}°C | L {low_c}°C",
            f"Sunset: {sunset_time}",
            f"Rain ~{int(avg_rain_chance)}% | Snow ~{int(avg_snow_chance)}%",
        ]

        return "\n".join(pieces)

    except Exception as e:
        return f"Weather error: {e}"

print(get_weather_summary())
