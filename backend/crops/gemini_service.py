"""Server-only Gemini integration for educational, text-only agronomy guidance.

The crop scores remain deterministic. Gemini offers an explanation, not a calibrated
prediction, disease diagnosis, fertilizer prescription or live weather measurement.
"""
import logging
import os
import re
import requests

logger = logging.getLogger(__name__)

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"


class GeminiUnavailable(Exception):
    """Safe-to-display service failure without exposing provider credentials."""


def _extract_error_message(response):
    try:
        payload = response.json()
        message = payload.get("error", {}).get("message")
        if isinstance(message, str):
            return message.strip()
    except ValueError:
        pass
    return ""


def generate_advice(topic, soil, crop=None, recommendations=None, weather=None):
    key = os.getenv("GEMINI_API_KEY", "").strip().strip('"').strip("'")
    if not key or key.lower() in {"your_key_here", "paste_your_gemini_api_key_here"}:
        raise GeminiUnavailable("Gemini is not configured. Add GEMINI_API_KEY in backend/.env and restart Django.")
    model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip().strip('"').strip("'") or DEFAULT_GEMINI_MODEL
    # Prevent accidental arbitrary host/path injection via the configured model.
    if not re.fullmatch(r"[a-zA-Z0-9_.-]{1,80}", model):
        raise GeminiUnavailable("Invalid GEMINI_MODEL in backend/.env.")
    if topic not in {"soil", "crops", "care", "weather"}:
        raise ValueError("Unsupported topic")

    facts = (f"Soil pH: {soil.soil_ph if soil.soil_ph is not None else 'unknown'}; "
             f"moisture: {soil.moisture if soil.moisture is not None else 'unknown'} percent; "
             f"soil type: {soil.soil_type}; "
             f"N, P, K reported without units: {soil.nitrogen}, {soil.phosphorus}, {soil.potassium}. "
             "NPK values cannot determine deficiency or fertilizer amounts without lab units. ")
    if topic == "soil":
        request = "Explain pH and moisture limitations and two safe next checks, in 3-5 short sentences."
    elif topic == "crops":
        crop_names = ", ".join(item["name"] for item in (recommendations or [])[:6])
        request = (f"Explain cautiously why these rule-based crop candidates could be considered: {crop_names}. "
                   "Mention region, season, variety and field validation are missing. 3-5 short sentences.")
    elif topic == "weather":
        if not weather:
            raise ValueError("Weather information required")
        current = weather["current"]
        days = weather["forecast"][:3]
        facts += (f"Open-Meteo forecast for {weather['location']['name']}, {weather['location']['country']}: "
                  f"temperature {current.get('temperature_c')} C, humidity {current.get('humidity_pct')}%; "
                  f"upcoming rainfall estimates by date (mm, probability %): "
                  + "; ".join(f"{d['date']}: {d.get('rain_mm')} mm, {d.get('rain_probability_pct')}%" for d in days) + ". ")
        request = ("Give 4-6 sentences of educational, weather-aware irrigation guidance using ONLY supplied weather and soil figures. "
                   "Explain why field moisture, crop growth stage and local observations must be checked before watering. "
                   "Never give specific irrigation amounts or intervals.")
    else:
        request = (f"Write 4-6 sentences of non-prescriptive care guidance for {crop['name']}. "
                   "Cover irrigation checking, drainage, fertilizer-testing and pest prevention. "
                   "Do not prescribe a precise water volume, dose, chemical or frequency.")
    instruction = ("You are an agricultural EDUCATION assistant for a student project. "
                   "Use ONLY the supplied measurements and any explicit Open-Meteo forecast data as evidence; do not invent weather, location, "
                   "crop stage, sensor readings, lab thresholds or research citations. "
                   "No definite disease diagnosis or pesticide/fertilizer dosage. "
                   "Do not present this as a scientifically validated prediction. "
                   "Clearly say recommendations require local verification. "
                   "Plain English text, no markdown tables or HTML. ")
    body = {
        "systemInstruction": {"parts": [{"text": instruction}]},
        "contents": [{"role": "user", "parts": [{"text": facts + request}]}],
        "generationConfig": {"maxOutputTokens": 2048},
    }
    try:
        response = requests.post(
            GEMINI_ENDPOINT.format(model=model),
            headers={"x-goog-api-key": key, "Content-Type": "application/json"},
            json=body, timeout=22,
        )
        if response.status_code in {400, 401, 403}:
            detail = _extract_error_message(response)
            logger.warning("Gemini request rejected (%s) for model %s: %s", response.status_code, model, detail or "no detail")
            raise GeminiUnavailable("Gemini rejected the request or API key. Check your Gemini key and model access.")
        if response.status_code == 404:
            detail = _extract_error_message(response)
            logger.warning("Gemini model not found (404) for model %s: %s", model, detail or "no detail")
            raise GeminiUnavailable(f"Gemini model '{model}' is unavailable. Update GEMINI_MODEL in backend/.env (e.g. {DEFAULT_GEMINI_MODEL}).")
        if response.status_code == 429:
            logger.warning("Gemini rate limit/quota reached (429) for model %s", model)
            raise GeminiUnavailable("Gemini rate limit reached. Try again later; the rule-based results remain available.")
        response.raise_for_status()
        data = response.json()
        text = "\n".join(
            part.get("text", "")
            for candidate in data.get("candidates", [])[:1]
            for part in candidate.get("content", {}).get("parts", [])
            if isinstance(part.get("text"), str) and not part.get("thought")
        ).strip()
        if not text:
            raise GeminiUnavailable("Gemini did not return usable guidance. The basic results are still available.")
        return {"text": text[:3500], "provider": "Google Gemini", "model": model,
                "disclaimer": "AI-generated educational guidance; verify with local agricultural experts. Weather forecasts are model-based; no soil sensor or validated prediction model."}
    except requests.Timeout as exc:
        raise GeminiUnavailable("Gemini timed out. Please retry; basic results still work.") from exc
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Gemini request failed for model %s: %s", model, exc)
        raise GeminiUnavailable("Gemini is temporarily unavailable. Basic results still work.") from exc