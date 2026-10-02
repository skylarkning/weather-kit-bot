"""Open-Meteo adapter for downtown Toronto's daily weather."""

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
TORONTO_DOWNTOWN = {"latitude": 43.6532, "longitude": -79.3832}

WEATHER_CODES = {
    0: ("Clear sky", "clear"), 1: ("Mostly clear", "clear"), 2: ("Partly cloudy", "cloudy"),
    3: ("Overcast", "cloudy"), 45: ("Foggy", "fog"), 48: ("Icy fog", "fog"),
    51: ("Light drizzle", "rain"), 53: ("Drizzle", "rain"), 55: ("Heavy drizzle", "rain"),
    56: ("Freezing drizzle", "rain"), 57: ("Heavy freezing drizzle", "rain"),
    66: ("Freezing rain", "rain"), 67: ("Heavy freezing rain", "rain"),
    61: ("Light rain", "rain"), 63: ("Rain", "rain"), 65: ("Heavy rain", "rain"),
    71: ("Light snow", "snow"), 73: ("Snow", "snow"), 75: ("Heavy snow", "snow"),
    77: ("Snow grains", "snow"), 85: ("Snow showers", "snow"), 86: ("Heavy snow showers", "snow"),
    80: ("Rain showers", "rain"), 81: ("Rain showers", "rain"), 82: ("Heavy showers", "rain"),
    95: ("Thunderstorms", "storm"), 96: ("Thunderstorms with hail", "storm"), 99: ("Thunderstorms with hail", "storm"),
}


def forecast_params():
    return {
        **TORONTO_DOWNTOWN,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset",
        "hourly": "temperature_2m,weather_code,relative_humidity_2m,wind_speed_10m,apparent_temperature,uv_index,visibility",
        "timezone": "America/Toronto",
    }
async def get_toronto_forecast(session):
    async with session.get(WEATHER_URL, params=forecast_params(), timeout=12) as response:
        response.raise_for_status()
        data = await response.json()
    return forecast_from_payload(data)


def forecast_from_payload(data):
    daily, hourly = data["daily"], data["hourly"]
    description, kind = WEATHER_CODES.get(daily["weather_code"][0], ("Toronto weather", "cloudy"))
    today = daily["time"][0]
    indices = [i for i, stamp in enumerate(hourly["time"]) if stamp.startswith(today) and 7 <= int(stamp[11:13]) <= 18]
    current = indices[0] if indices else 0
    return {
        "description": description, "kind": kind, "code": daily["weather_code"][0],
        "high": round(daily["temperature_2m_max"][0]), "low": round(daily["temperature_2m_min"][0]),
        "precipitation": daily["precipitation_probability_max"][0], "date": today,
        "temperature": round(hourly["temperature_2m"][current]),
        "feels_like": round(hourly["apparent_temperature"][current]),
        "humidity": hourly["relative_humidity_2m"][current], "wind": round(hourly["wind_speed_10m"][current]),
        "uv_index": round(hourly["uv_index"][current]), "visibility": round(hourly["visibility"][current] / 1000),
        "sunrise": daily["sunrise"][0][11:], "sunset": daily["sunset"][0][11:],
        "hourly": [{"time": hourly["time"][i][11:], "temp": round(hourly["temperature_2m"][i]), "code": hourly["weather_code"][i]} for i in indices],
    }
