"""Server-only Gemini integration for educational, text-only agronomy guidance
and AI-generated crop recommendations / care plans.
"""
import json
import logging
import os
import re
import requests
from django.core.cache import cache

logger = logging.getLogger(__name__)

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"


class GeminiUnavailable(Exception):
    """Safe-to-display service failure without exposing provider credentials."""


def _get_api_config():
    key = os.getenv("GEMINI_API_KEY", "").strip().strip('"').strip("'")
    if not key or key.lower() in {"your_key_here", "paste_your_gemini_api_key_here"}:
        raise GeminiUnavailable("Gemini is not configured. Add GEMINI_API_KEY in backend/.env and restart Django.")
    model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip().strip('"').strip("'") or DEFAULT_GEMINI_MODEL
    if not re.fullmatch(r"[a-zA-Z0-9_.-]{1,80}", model):
        raise GeminiUnavailable("Invalid GEMINI_MODEL in backend/.env.")
    return key, model


def _extract_error_message(response):
    try:
        payload = response.json()
        message = payload.get("error", {}).get("message")
        if isinstance(message, str):
            return message.strip()
    except ValueError:
        pass
    return ""


def _post_gemini(key, model, body):
    try:
        response = requests.post(
            GEMINI_ENDPOINT.format(model=model),
            headers={"x-goog-api-key": key, "Content-Type": "application/json"},
            json=body,
            timeout=25,
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
            raise GeminiUnavailable("Gemini rate limit reached. Try again later; the fallback results remain available.")
        response.raise_for_status()
        data = response.json()
        text = "\n".join(
            part.get("text", "")
            for candidate in data.get("candidates", [])[:1]
            for part in candidate.get("content", {}).get("parts", [])
            if isinstance(part.get("text"), str) and not part.get("thought")
        ).strip()
        if not text:
            raise GeminiUnavailable("Gemini did not return usable guidance.")
        return text
    except requests.Timeout as exc:
        raise GeminiUnavailable("Gemini timed out. Please retry.") from exc
    except (requests.RequestException, ValueError) as exc:
        logger.warning("Gemini request failed for model %s: %s", model, exc)
        raise GeminiUnavailable("Gemini is temporarily unavailable.") from exc


def generate_ai_recommendations(soil, force_refresh=False, cache_only=False):
    """Use Gemini to generate 6 tailored crop recommendations and care plans for the user's soil."""
    key, model = _get_api_config()
    cache_key = f"agrivision:ai_recs:{soil.id}:{model}"
    if not force_refresh:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
    if cache_only:
        raise GeminiUnavailable("AI recommendations have not been generated yet.")

    soil_summary = (
        f"Soil type: {soil.soil_type or 'unknown'}; "
        f"Soil pH: {soil.soil_ph if soil.soil_ph is not None else 'unknown'}; "
        f"Moisture: {soil.moisture if soil.moisture is not None else 'unknown'}%; "
        f"Nitrogen (N): {soil.nitrogen if soil.nitrogen is not None else 'unknown'}; "
        f"Phosphorus (P): {soil.phosphorus if soil.phosphorus is not None else 'unknown'}; "
        f"Potassium (K): {soil.potassium if soil.potassium is not None else 'unknown'}; "
        f"Location: {soil.location or 'not specified'}."
    )

    instruction = (
        "You are an expert agricultural AI assistant. Given the user's soil measurements and location, "
        "recommend the 6 best-suited crops ranked from highest suitability score (0-100) to lowest. "
        "Return ONLY valid JSON matching this exact structure: "
        '{"crops": [{"name": "Crop Name", "icon": "🌾", "score": 92, "water": "Moderate", '
        '"temperature": "20-32°C", "duration": "100-130 days", '
        '"reasons": ["Reason 1 referencing soil pH/type/moisture", "Reason 2 referencing location/nutrients"], '
        '"care_plan": {"fertilizer": "2-3 sentences of safe nutrient & soil-testing guidance", '
        '"irrigation": "2-3 sentences of moisture & drainage guidance", '
        '"temperature": "1-2 sentences on ideal temperature & season", '
        '"protection": "2-3 sentences on preventive pest/disease monitoring"}}]}. '
        "Do not prescribe exact chemical pesticide dosages or exact litres per field. "
        "Use a single relevant plant/food emoji for each icon."
    )

    body = {
        "systemInstruction": {"parts": [{"text": instruction}]},
        "contents": [{"role": "user", "parts": [{"text": f"Recommend 6 crops for this soil profile: {soil_summary}"}]}],
        "generationConfig": {
            "maxOutputTokens": 4096,
            "responseMimeType": "application/json",
        },
    }

    raw_text = _post_gemini(key, model, body)
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text.strip(), flags=re.IGNORECASE | re.MULTILINE).strip()
    try:
        parsed = json.loads(cleaned)
    except ValueError as exc:
        logger.warning("Gemini returned invalid JSON for recommendations: %s", exc)
        raise GeminiUnavailable("Gemini returned an unreadable recommendation format.") from exc

    raw_crops = parsed.get("crops")
    if not isinstance(raw_crops, list) or not raw_crops:
        raise GeminiUnavailable("Gemini did not return crop recommendations.")

    normalized = []
    for item in raw_crops[:6]:
        if not isinstance(item, dict) or not item.get("name"):
            continue
        score = item.get("score")
        try:
            score = max(0, min(100, int(round(float(score))))) if score is not None else None
        except (TypeError, ValueError):
            score = None
        reasons = item.get("reasons")
        if not isinstance(reasons, list):
            reasons = [str(reasons)] if reasons else []
        cp = item.get("care_plan") if isinstance(item.get("care_plan"), dict) else {}
        duration = str(item.get("duration") or "90–120 days")
        normalized.append({
            "name": str(item["name"]).strip(),
            "icon": str(item.get("icon") or "🌱").strip(),
            "score": score,
            "water": str(item.get("water") or "Moderate"),
            "temperature": str(item.get("temperature") or "18–32°C"),
            "duration": duration,
            "reasons": [str(r) for r in reasons[:4]],
            "care_plan": {
                "crop": str(item["name"]).strip(),
                "fertilizer": str(cp.get("fertilizer") or "Verify soil NPK units with a local lab before applying fertilizer."),
                "irrigation": str(cp.get("irrigation") or "Check root-zone moisture and local rainfall before irrigating."),
                "temperature": str(cp.get("temperature") or f"Typical growing range: {item.get('temperature') or '18–32°C'}."),
                "protection": str(cp.get("protection") or "Monitor leaves and roots regularly and use locally approved preventive practices."),
                "duration": duration,
                "disclaimer": "AI-generated educational crop care guidance; verify locally with agricultural experts.",
            },
        })

    if not normalized:
        raise GeminiUnavailable("Gemini did not return valid crop entries.")

    normalized.sort(key=lambda x: x["score"] if x["score"] is not None else -1, reverse=True)
    result = {"crops": normalized, "model": model}
    cache.set(cache_key, result, timeout=1800)
    return result


def generate_advice(topic, soil, crop=None, recommendations=None, weather=None):
    key, model = _get_api_config()
    if topic not in {"soil", "crops", "care", "weather"}:
        raise ValueError("Unsupported topic")

    facts = (f"Soil pH: {soil.soil_ph if soil.soil_ph is not None else 'unknown'}; "
             f"moisture: {soil.moisture if soil.moisture is not None else 'unknown'} percent; "
             f"soil type: {soil.soil_type}; "
             f"location: {soil.location or 'unknown'}; "
             f"N, P, K reported without units: {soil.nitrogen}, {soil.phosphorus}, {soil.potassium}. "
             "NPK values cannot determine deficiency or fertilizer amounts without lab units. ")
    if topic == "soil":
        request = "Explain pH, moisture, and soil type implications and two safe next checks, in 3-5 short sentences."
    elif topic == "crops":
        crop_names = ", ".join(item["name"] for item in (recommendations or [])[:6])
        request = (f"Explain why these AI-recommended crops fit this soil and location: {crop_names}. "
                   "Mention season, variety, and local field verification. 3-5 short sentences.")
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
    instruction = ("You are an agricultural EDUCATION assistant. "
                   "Use ONLY the supplied measurements and any explicit Open-Meteo forecast data as evidence; do not invent sensor readings. "
                   "No definite disease diagnosis or pesticide/fertilizer dosage. "
                   "Clearly say recommendations require local verification. "
                   "Plain English text, no markdown tables or HTML. ")
    body = {
        "systemInstruction": {"parts": [{"text": instruction}]},
        "contents": [{"role": "user", "parts": [{"text": facts + request}]}],
        "generationConfig": {"maxOutputTokens": 2048},
    }
    text = _post_gemini(key, model, body)
    return {
        "text": text[:3500],
        "provider": "Google Gemini",
        "model": model,
        "disclaimer": "AI-generated educational guidance; verify with local agricultural experts.",
    }