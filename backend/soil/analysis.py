"""Illustrative soil screening only, not laboratory nutrient interpretation.
NPK concentrations depend on measurement unit, extraction method and lab reference ranges.
"""
def analyze_soil(soil):
    notes = []
    ph = soil.soil_ph
    moisture = soil.moisture
    if ph is None:
        notes.append("Enter a measured soil pH for acidity guidance.")
        acidity = "Unknown"
    elif ph < 5.5:
        acidity = "Strongly acidic"
        notes.append("Soil is strongly acidic; check crop tolerance and consult a soil-testing lab before amending.")
    elif ph < 6.5:
        acidity = "Slightly acidic"
    elif ph <= 7.5:
        acidity = "Near neutral"
    elif ph <= 8.5:
        acidity = "Alkaline"
        notes.append("High pH can affect nutrient availability; consider local agronomic advice.")
    else:
        acidity = "Strongly alkaline"
        notes.append("Very high pH: confirm the measurement with a certified soil test.")
    if moisture is None:
        water = "Unknown"
    elif moisture < 25:
        water = "Low (illustrative)"
        notes.append("Moisture appears low; check plant needs and soil depth before irrigation.")
    elif moisture > 75:
        water = "High (illustrative)"
        notes.append("Moisture appears high; inspect drainage and root conditions.")
    else:
        water = "Moderate (illustrative)"
    if any(getattr(soil, key) is not None for key in ("nitrogen", "phosphorus", "potassium")):
        notes.append("NPK values are stored but cannot be classified without measurement units and laboratory reference ranges.")
    return {"acidity": acidity, "moisture_status": water, "notes": notes,
            "disclaimer": "Preliminary educational screening, not a laboratory soil report or fertilizer prescription."}
