"""Open-Meteo weather lookups: no API key, server-side only, 10-minute cache."""
import re
import requests
from django.core.cache import cache

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

class WeatherUnavailable(Exception):
    pass

def city_name(value):
    city = str(value or "").strip()
    if not 2 <= len(city) <= 80 or not re.fullmatch(r"[\w\s.,'()\-]+", city, re.UNICODE):
        raise ValueError("Enter a valid city or town (2–80 characters).")
    return city

def _json(url, params):
    try:
        response = requests.get(url, params=params, timeout=12)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict) or data.get("error"):
            raise WeatherUnavailable("Weather provider returned an invalid response.")
        return data
    except (requests.RequestException, ValueError) as exc:
        raise WeatherUnavailable("Weather service is temporarily unavailable. Please retry.") from exc

def fetch_weather(city):
    city = city_name(city)
    cache_key = "agrivision-weather:" + city.casefold()
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    geo = _json(GEOCODE_URL, {"name": city, "count": 1, "language": "en", "format": "json"})
    matches = geo.get("results") or []
    if not matches:
        raise WeatherUnavailable("Location not found. Try a nearby city or a more specific name.")
    place = matches[0]
    try:
        latitude, longitude = float(place["latitude"]), float(place["longitude"])
    except (KeyError, TypeError, ValueError) as exc:
        raise WeatherUnavailable("Weather location data is incomplete.") from exc
    raw = _json(FORECAST_URL, {
        "latitude": latitude, "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max",
        "timezone": "auto", "forecast_days": 7,
    })
    current, daily = raw.get("current") or {}, raw.get("daily") or {}
    dates = daily.get("time") or []
    forecast = [{"date": date,
                 "weather_code": (daily.get("weather_code") or [None]*len(dates))[i],
                 "temperature_max_c": (daily.get("temperature_2m_max") or [None]*len(dates))[i],
                 "temperature_min_c": (daily.get("temperature_2m_min") or [None]*len(dates))[i],
                 "rain_mm": (daily.get("precipitation_sum") or [None]*len(dates))[i],
                 "rain_probability_pct": (daily.get("precipitation_probability_max") or [None]*len(dates))[i]}
                for i, date in enumerate(dates[:7])]
    if not forecast or not current:
        raise WeatherUnavailable("Weather data is incomplete. Try again later.")
    result = {
        "location": {"name":place.get("name"), "region":place.get("admin1"), "country":place.get("country"), "latitude":latitude, "longitude":longitude},
        "current": {"time":current.get("time"), "temperature_c":current.get("temperature_2m"),
                    "humidity_pct":current.get("relative_humidity_2m"), "precipitation_mm":current.get("precipitation"),
                    "wind_kmh":current.get("wind_speed_10m"), "weather_code":current.get("weather_code")},
        "forecast": forecast, "source": "Open-Meteo", "timezone":raw.get("timezone"),
        "disclaimer": "Model-based weather data, not a field measurement. Verify local conditions before irrigating."
    }
    cache.set(cache_key, result, timeout=600)
    return result

def irrigation_note(weather, moisture=None):
    days = weather.get("forecast", [])[:2]
    rain = [d.get("rain_mm") for d in days]
    chance = [d.get("rain_probability_pct") for d in days]
    meaningful_rain = any(isinstance(x,(int,float)) and x >= 5 for x in rain)
    likely_rain = any(isinstance(x,(int,float)) and x >= 70 for x in chance)
    if meaningful_rain or likely_rain:
        advice = "Rain is forecast in the next two days. Check field moisture and forecast updates before adding irrigation; ensure drainage."
    else:
        advice = "No substantial rain is indicated in the next two days. Check actual root-zone soil moisture before deciding whether irrigation is needed."
    if moisture is not None:
        try:
            level = float(moisture)
            if level < 25:
                advice += " Your entered moisture is low; confirm with an in-field measurement."
            elif level > 75:
                advice += " Your entered moisture is high; avoid watering until drainage and root-zone conditions are checked."
        except (ValueError, TypeError):
            pass
    return advice + " This is general guidance, not a litres-per-field prescription."
