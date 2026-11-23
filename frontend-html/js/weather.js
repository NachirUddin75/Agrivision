document.addEventListener("DOMContentLoaded", async () => {
    const form = document.getElementById("weather-form");
    const input = document.getElementById("weather-city");
    const status = document.getElementById("weather-status");
    const results = document.getElementById("weather-results");
    const button = document.getElementById("weather-submit");
    const aiButton = document.getElementById("weather-ai-button");
    const copyButton = document.getElementById("weather-copy-button");
    const output = document.getElementById("weather-ai-output");
    let selectedCity = null;

    function incrementAiInsights() {
        const current = parseInt(localStorage.getItem("agrivision_ai_insights_count") || "0", 10);
        localStorage.setItem("agrivision_ai_insights_count", String((Number.isFinite(current) ? current : 0) + 1));
    }

    const weatherDescription = (code) => {
        if (code === 0) return "Clear";
        if ([1, 2, 3].includes(code)) return "Cloudy / partly cloudy";
        if ([45, 48].includes(code)) return "Fog";
        if ([51, 53, 55, 56, 57].includes(code)) return "Drizzle";
        if ([61, 63, 65, 66, 67, 80, 81, 82].includes(code)) return "Rain";
        if ([71, 73, 75, 77, 85, 86].includes(code)) return "Snow";
        if ([95, 96, 99].includes(code)) return "Thunderstorm";
        return "Not specified";
    };

    function metric(title, value, iconClass) {
        const col = document.createElement("div");
        col.className = "col-sm-6 col-lg-3";
        const card = document.createElement("div");
        card.className = "agr-weather-metric-card";
        const label = document.createElement("div");
        label.className = "text-secondary small fw-semibold d-flex align-items-center gap-2";
        const icon = document.createElement("i");
        icon.className = `bi ${iconClass} text-success`;
        label.append(icon, document.createTextNode(title));

        const number = document.createElement("div");
        number.className = "h3 fw-bold text-dark mt-2 mb-0";
        number.textContent = value;

        card.append(label, number);
        col.append(card);
        return col;
    }

    async function loadWeatherForCity(city) {
        selectedCity = null;
        results.hidden = true;
        output.textContent = "";
        output.classList.add("d-none");
        if (copyButton) copyButton.classList.add("d-none");

        button.disabled = true;
        status.textContent = `Loading local forecast for ${city}…`;

        const result = await apiRequest(`/crops/weather/?city=${encodeURIComponent(city)}`);
        button.disabled = false;

        if (!result.ok) {
            status.textContent = result.data.detail || result.data.city || result.data.message || "Weather unavailable. Please try again.";
            return;
        }

        const data = result.data;
        selectedCity = city;
        results.hidden = false;

        const place = data.location;
        document.getElementById("weather-place").textContent = [place.name, place.region, place.country].filter(Boolean).join(", ");
        status.textContent = `Forecast updated for ${place.name}. Timezone: ${data.timezone || "local"}.`;

        const current = document.getElementById("weather-current");
        current.replaceChildren(
            metric("Temperature", data.current.temperature_c == null ? "N/A" : `${data.current.temperature_c} °C`, "bi-thermometer-half"),
            metric("Humidity", data.current.humidity_pct == null ? "N/A" : `${data.current.humidity_pct}%`, "bi-moisture"),
            metric("Precipitation", data.current.precipitation_mm == null ? "N/A" : `${data.current.precipitation_mm} mm`, "bi-cloud-rain"),
            metric("Wind", data.current.wind_kmh == null ? "N/A" : `${data.current.wind_kmh} km/h`, "bi-wind")
        );

        const tbody = document.getElementById("weather-days");
        tbody.replaceChildren();
        for (const day of data.forecast) {
            const row = document.createElement("tr");
            const cells = [
                day.date,
                weatherDescription(day.weather_code),
                `${day.temperature_min_c ?? "–"} / ${day.temperature_max_c ?? "–"} °C`,
                day.rain_mm == null ? "–" : String(day.rain_mm),
                day.rain_probability_pct == null ? "–" : `${day.rain_probability_pct}%`,
            ];
            cells.forEach((value) => {
                const td = document.createElement("td");
                td.textContent = value;
                row.append(td);
            });
            tbody.append(row);
        }

        document.getElementById("irrigation-note").textContent = data.irrigation_guidance;
    }

    document.querySelectorAll("[data-city]").forEach((chip) => {
        chip.addEventListener("click", () => {
            const city = chip.getAttribute("data-city");
            if (input) input.value = city;
            loadWeatherForCity(city);
        });
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const city = input.value.trim();
        if (!city) return;
        await loadWeatherForCity(city);
    });

    if (copyButton) {
        copyButton.addEventListener("click", async () => {
            if (!output.textContent) return;
            await navigator.clipboard.writeText(output.textContent);
            copyButton.textContent = "Copied!";
            setTimeout(() => { copyButton.textContent = "Copy Advice"; }, 1800);
        });
    }

    aiButton.addEventListener("click", async () => {
        if (!selectedCity) return;
        aiButton.disabled = true;
        aiButton.textContent = "Generating Gemini advice…";
        output.classList.remove("d-none");
        output.textContent = "Asking Google Gemini for weather-aware irrigation guidance…";

        const res = await apiRequest("/crops/gemini-advice/", {
            method: "POST",
            body: JSON.stringify({ topic: "weather", city: selectedCity }),
        });

        if (res.ok && res.data?.guidance) {
            incrementAiInsights();
            output.textContent = `${res.data.guidance.text}\n\n[${res.data.guidance.provider} · ${res.data.guidance.model}] ${res.data.guidance.disclaimer}`;
            if (copyButton) copyButton.classList.remove("d-none");
        } else {
            output.textContent = res.data?.detail || "Gemini advice unavailable. Forecast and basic irrigation guidance remain available. Create a soil analysis first if needed.";
        }

        aiButton.textContent = "✦ Generate Gemini Irrigation Advice";
        aiButton.disabled = false;
    });

    // Auto-load weather from latest soil analysis location if available
    if (input && !input.value.trim()) {
        const soilReply = await apiRequest("/soil/");
        if (soilReply.ok) {
            const items = Array.isArray(soilReply.data) ? soilReply.data : (soilReply.data.results || []);
            const loc = items[0]?.location;
            if (loc) {
                const city = String(loc).split(",")[0].trim();
                if (city) {
                    input.value = city;
                    loadWeatherForCity(city);
                }
            }
        }
    }
});
