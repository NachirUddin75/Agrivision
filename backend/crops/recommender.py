"""Transparent heuristic crop matching; NOT a trained ML model.
Ranges are illustrative and must be locally validated for agronomic decisions.
"""
CROPS = [
    {"name":"Rice", "icon":"🌾", "ph":(5.0,7.5), "soil":["clay","loamy","silty"], "moisture":(55,100), "temperature":"20–35°C", "water":"High", "duration":"100–150 days"},
    {"name":"Maize", "icon":"🌽", "ph":(5.5,7.5), "soil":["loamy","silty","black"], "moisture":(35,70), "temperature":"18–32°C", "water":"Moderate", "duration":"90–120 days"},
    {"name":"Tomato", "icon":"🍅", "ph":(6.0,7.0), "soil":["loamy","sandy"], "moisture":(35,70), "temperature":"18–28°C", "water":"Moderate", "duration":"75–100 days"},
    {"name":"Potato", "icon":"🥔", "ph":(5.0,6.5), "soil":["loamy","sandy"], "moisture":(35,75), "temperature":"15–22°C", "water":"Moderate", "duration":"90–120 days"},
    {"name":"Wheat", "icon":"🌿", "ph":(6.0,7.5), "soil":["loamy","clay","black"], "moisture":(25,65), "temperature":"15–25°C", "water":"Moderate", "duration":"110–140 days"},
    {"name":"Groundnut", "icon":"🥜", "ph":(5.8,7.2), "soil":["sandy","loamy","red"], "moisture":(25,65), "temperature":"25–35°C", "water":"Low to moderate", "duration":"100–130 days"},
]

def recommend(soil):
    results = []
    for crop in CROPS:
        points = 0
        possible = 0
        reasons = []
        if soil.soil_ph is not None:
            possible += 45
            lo, hi = crop["ph"]
            if lo <= soil.soil_ph <= hi:
                points += 45
                reasons.append("pH is within illustrative preferred range")
            else:
                distance = min(abs(soil.soil_ph - lo), abs(soil.soil_ph - hi))
                points += max(0, 45 - distance*30)
                reasons.append("pH differs from preferred range")
        if soil.soil_type and soil.soil_type != "other":
            possible += 30
            if soil.soil_type in crop["soil"]:
                points += 30
                reasons.append("soil type is a typical match")
            else:
                reasons.append("soil type is not a typical match")
        if soil.moisture is not None:
            possible += 25
            lo, hi = crop["moisture"]
            if lo <= soil.moisture <= hi:
                points += 25
                reasons.append("moisture is within illustrative range")
            else:
                distance = min(abs(soil.moisture-lo),abs(soil.moisture-hi))
                points += max(0,25-distance)
                reasons.append("moisture differs from illustrative range")
        score = round(100*points/possible) if possible else None
        results.append({**crop, "score":score, "reasons":reasons})
    results.sort(key=lambda x: x["score"] if x["score"] is not None else -1, reverse=True)
    return results

def care_plan(soil,crop):
    if crop is None:
        return None
    fertilizer = "Obtain a laboratory soil test with NPK units before deciding fertilizer type or dose."
    if soil.nitrogen is not None or soil.phosphorus is not None or soil.potassium is not None:
        fertilizer += " The supplied NPK numbers alone do not establish deficiency."
    irrigation = f"{crop['name']} generally has {crop['water'].lower()} water needs. Monitor root-zone moisture and local rainfall; avoid waterlogging."
    if soil.moisture is not None and soil.moisture < 25:
        irrigation += " Your reported moisture is low; check soil before irrigating."
    if soil.moisture is not None and soil.moisture > 75:
        irrigation += " Your reported moisture is high; check drainage before adding water."
    return {"crop":crop["name"], "fertilizer":fertilizer, "irrigation":irrigation,
            "temperature":f"Typical growing range (illustrative): {crop['temperature']}. Check variety and season locally.",
            "protection":"Inspect leaves and roots regularly, remove infected plant material carefully, encourage airflow, and use locally approved pest-management advice after identifying the cause.",
            "duration":crop["duration"], "disclaimer":"Educational guidance only; not an agronomic prescription. No ML model or live weather data is used."}
