document.addEventListener("DOMContentLoaded", function () {
    loadDashboardGreeting();
    loadAiStats();
    loadSoilActivity();
});

function loadDashboardGreeting() {
    const user = getCurrentUser() || {};
    const firstName = user.first_name || user.username || "Farmer";

    const welcomeName = document.getElementById("welcomeName");
    if (welcomeName) {
        welcomeName.textContent = firstName;
    }

    const greetingEl = document.getElementById("welcomeGreeting");
    if (greetingEl) {
        const hour = new Date().getHours();
        if (hour < 12) greetingEl.textContent = "Good morning";
        else if (hour < 17) greetingEl.textContent = "Good afternoon";
        else greetingEl.textContent = "Good evening";
    }

    const accountStatus = document.getElementById("statAccountStatus");
    if (accountStatus && user.is_verified === false) {
        accountStatus.textContent = "Pending";
    }
}

function loadAiStats() {
    const aiCountEl = document.getElementById("statAiCount");
    if (aiCountEl) {
        const count = parseInt(localStorage.getItem("agrivision_ai_insights_count") || "0", 10);
        aiCountEl.textContent = Number.isFinite(count) ? String(count) : "0";
    }
}

function capitalizeWord(value) {
    if (!value) return "—";
    return value.charAt(0).toUpperCase() + value.slice(1);
}

async function loadSoilActivity() {
    const holder = document.getElementById("soil-activity-list");
    const soilCountEl = document.getElementById("statSoilCount");
    const cropPlansEl = document.getElementById("statCropPlansCount");
    const aiStatusEl = document.getElementById("aiSystemStatus");

    const reply = await apiRequest("/soil/");
    if (!reply.ok) {
        if (holder) {
            holder.textContent = "Unable to load activity. Please log in and retry.";
        }
        return;
    }

    const items = Array.isArray(reply.data) ? reply.data : (reply.data.results || []);

    if (soilCountEl) soilCountEl.textContent = String(items.length);
    if (cropPlansEl) cropPlansEl.textContent = items.length > 0 ? "6" : "0";
    if (aiStatusEl && items.length > 0) {
        aiStatusEl.textContent = `${items.length} soil record(s) ready for Gemini AI explanations.`;
    }

    if (items.length > 0) {
        const latest = items[0];
        const badge = document.getElementById("overviewStatusBadge");
        if (badge) {
            badge.textContent = "Latest reading active";
            badge.className = "badge bg-success-subtle text-success-emphasis rounded-pill px-3 py-2 fw-semibold";
        }

        const emptyState = document.getElementById("overviewEmptyState");
        const latestState = document.getElementById("overviewLatestState");
        if (emptyState) emptyState.classList.add("d-none");
        if (latestState) latestState.classList.remove("d-none");

        const titleEl = document.getElementById("overviewLatestTitle");
        if (titleEl) {
            titleEl.textContent = `${capitalizeWord(latest.soil_type)} Soil — ${latest.location || "Field location not specified"}`;
        }

        const metaEl = document.getElementById("overviewLatestMeta");
        if (metaEl) {
            metaEl.textContent = `Recorded ${new Date(latest.created_at).toLocaleString()} · ${latest.assessment?.acidity || "Unknown pH"} · ${latest.assessment?.moisture_status || "Unknown moisture"}`;
        }

        const notesEl = document.getElementById("overviewLatestNotes");
        if (notesEl) {
            const notes = latest.assessment?.notes || [];
            notesEl.textContent = notes.length ? notes.join(" ") : (latest.assessment?.disclaimer || "Preliminary screening complete.");
        }

        const recLink = document.getElementById("overviewRecommendLink");
        if (recLink) {
            recLink.href = `crop-recommendation.html?soil_id=${encodeURIComponent(latest.id)}`;
        }

        const phEl = document.getElementById("overviewPh");
        const moistureEl = document.getElementById("overviewMoisture");
        const soilTypeEl = document.getElementById("overviewSoilType");
        if (phEl) phEl.textContent = latest.soil_ph != null ? String(latest.soil_ph) : "—";
        if (moistureEl) moistureEl.textContent = latest.moisture != null ? `${latest.moisture}%` : "—";
        if (soilTypeEl) soilTypeEl.textContent = capitalizeWord(latest.soil_type);

        // Visual pH & Moisture gauges
        const phLabel = document.getElementById("overviewPhLabel");
        const phMarker = document.getElementById("overviewPhMarker");
        if (phLabel && phMarker && latest.soil_ph != null) {
            const pct = Math.max(0, Math.min(100, (Number(latest.soil_ph) / 14) * 100));
            phMarker.style.left = `${pct}%`;
            phLabel.textContent = `${latest.soil_ph} (${latest.assessment?.acidity || ""})`;
        }

        const moistureLabel = document.getElementById("overviewMoistureLabel");
        const moistureBar = document.getElementById("overviewMoistureBar");
        if (moistureLabel && moistureBar && latest.moisture != null) {
            const pct = Math.max(0, Math.min(100, Number(latest.moisture)));
            moistureBar.style.width = `${pct}%`;
            moistureLabel.textContent = `${latest.moisture}%`;
        }
    }

    if (!holder) return;
    holder.replaceChildren();

    if (!items.length) {
        const empty = document.createElement("p");
        empty.className = "text-secondary small mb-0";
        empty.textContent = "No recent analyses yet. Start a soil analysis to see your history here.";
        holder.append(empty);
        return;
    }

    const listWrap = document.createElement("div");
    listWrap.className = "d-flex flex-column gap-3";

    for (const record of items.slice(0, 8)) {
        const card = document.createElement("div");
        card.className = "agr-activity-item d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3";

        const info = document.createElement("div");
        const label = document.createElement("div");
        label.className = "fw-bold text-dark";
        label.textContent = `${capitalizeWord(record.soil_type)} soil · ${record.location || "Location not provided"}`;

        const detail = document.createElement("div");
        detail.className = "small text-secondary mt-1";
        detail.textContent = `${new Date(record.created_at).toLocaleString()} · pH: ${record.soil_ph ?? "—"} · Moisture: ${record.moisture ?? "—"}% · ${record.assessment?.acidity || "Not assessed"}`;

        info.append(label, detail);

        const actions = document.createElement("div");
        actions.className = "d-flex flex-wrap gap-2";

        const recBtn = document.createElement("a");
        recBtn.href = `crop-recommendation.html?soil_id=${encodeURIComponent(record.id)}`;
        recBtn.className = "btn btn-sm btn-outline-success fw-semibold";
        recBtn.textContent = "Recommendations →";

        const careBtn = document.createElement("a");
        careBtn.href = `crop-care.html?soil_id=${encodeURIComponent(record.id)}`;
        careBtn.className = "btn btn-sm btn-light border fw-semibold";
        careBtn.textContent = "Crop Care";

        actions.append(recBtn, careBtn);
        card.append(info, actions);
        listWrap.append(card);
    }

    holder.append(listWrap);
}
