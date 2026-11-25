document.addEventListener("DOMContentLoaded", async () => {
    const target = document.getElementById("crop-results");
    const message = document.getElementById("crop-status");
    const advicePanel = document.getElementById("gemini-advice");
    const switcherBar = document.getElementById("soil-switcher-bar");
    const soilSelector = document.getElementById("soil-selector");
    const cropSelector = document.getElementById("crop-selector");
    const refreshBtn = document.getElementById("refresh-ai-btn");

    const params = new URLSearchParams(window.location.search);
    const isCare = document.body.dataset.cropPage === "care";

    function incrementAiInsights() {
        const current = parseInt(localStorage.getItem("agrivision_ai_insights_count") || "0", 10);
        localStorage.setItem("agrivision_ai_insights_count", String((Number.isFinite(current) ? current : 0) + 1));
    }

    const soilListReply = await apiRequest("/soil/");
    const soilRecords = soilListReply.ok
        ? (Array.isArray(soilListReply.data) ? soilListReply.data : (soilListReply.data.results || []))
        : [];

    if (switcherBar && soilSelector && soilRecords.length > 0) {
        switcherBar.classList.remove("d-none");
        soilSelector.replaceChildren();
        for (const rec of soilRecords) {
            const opt = document.createElement("option");
            opt.value = String(rec.id);
            const labelType = rec.soil_type ? rec.soil_type.charAt(0).toUpperCase() + rec.soil_type.slice(1) : "Soil";
            opt.textContent = `#${rec.id} · ${labelType} · pH ${rec.soil_ph ?? "—"} · ${rec.location || "No location"}`;
            soilSelector.append(opt);
        }
        if (params.get("soil_id")) {
            soilSelector.value = params.get("soil_id");
        }
        soilSelector.addEventListener("change", () => {
            const next = new URLSearchParams(window.location.search);
            next.set("soil_id", soilSelector.value);
            next.delete("refresh");
            window.location.search = next.toString();
        });
    }

    if (refreshBtn) {
        refreshBtn.addEventListener("click", () => {
            const next = new URLSearchParams(window.location.search);
            next.set("refresh", "1");
            window.location.search = next.toString();
        });
    }

    const q = new URLSearchParams();
    if (params.get("soil_id")) q.set("soil_id", params.get("soil_id"));
    if (params.get("crop")) q.set("crop", params.get("crop"));
    if (params.get("refresh") === "1") q.set("refresh", "1");

    const reply = await apiRequest(`/crops/recommendations/?${q.toString()}`);
    if (!reply.ok) {
        message.className = "alert alert-danger rounded-4";
        message.textContent = reply.status === 401
            ? "Please sign in again."
            : (reply.data.detail || "Could not retrieve recommendations.");
        return;
    }

    if (!reply.data.analysis) {
        message.className = "alert alert-warning rounded-4";
        message.textContent = "No soil analysis found. Add a soil analysis first to see AI recommendations.";
        const col = document.createElement("div");
        col.className = "col-12";
        const a = document.createElement("a");
        a.href = "soil-analysis.html";
        a.className = "btn btn-success fw-semibold";
        a.textContent = "Analyze Soil →";
        col.append(a);
        target.append(col);
        return;
    }

    if (isCare && cropSelector && Array.isArray(reply.data.recommendations)) {
        cropSelector.replaceChildren();
        for (const item of reply.data.recommendations) {
            const opt = document.createElement("option");
            opt.value = item.name;
            opt.textContent = `${item.icon} ${item.name}${item.score !== null ? ` (${item.score}/100)` : ""}`;
            cropSelector.append(opt);
        }
        if (reply.data.care_plan?.crop) {
            cropSelector.value = reply.data.care_plan.crop;
        }
        cropSelector.addEventListener("change", () => {
            const next = new URLSearchParams(window.location.search);
            next.set("soil_id", String(reply.data.analysis.id));
            next.set("crop", cropSelector.value);
            next.delete("refresh");
            window.location.search = next.toString();
        });
    }

    if (advicePanel) {
        advicePanel.replaceChildren();

        const btnGroup = document.createElement("div");
        btnGroup.className = "d-flex flex-wrap gap-2";

        const button = document.createElement("button");
        button.className = "btn btn-success fw-semibold";
        button.type = "button";
        button.textContent = isCare
            ? "✦ Generate Gemini Crop-Care Advice"
            : "✦ Explain Recommendations with Gemini AI";

        const copyBtn = document.createElement("button");
        copyBtn.type = "button";
        copyBtn.className = "btn btn-light border fw-semibold d-none";
        copyBtn.textContent = "Copy Advice";

        btnGroup.append(button, copyBtn);

        const output = document.createElement("div");
        output.className = "agr-ai-output-box mt-3 d-none";
        output.setAttribute("aria-live", "polite");

        copyBtn.addEventListener("click", async () => {
            if (!output.textContent) return;
            await navigator.clipboard.writeText(output.textContent);
            copyBtn.textContent = "Copied!";
            setTimeout(() => { copyBtn.textContent = "Copy Advice"; }, 1800);
        });

        button.addEventListener("click", async () => {
            button.disabled = true;
            const originalLabel = button.textContent;
            button.textContent = "Generating Gemini guidance…";
            output.classList.remove("d-none");
            output.textContent = "Asking Google Gemini for educational agronomy guidance…";

            const payload = {
                topic: isCare ? "care" : "crops",
                soil_id: reply.data.analysis.id,
            };
            if (isCare) payload.crop = reply.data.care_plan?.crop;

            const ai = await apiRequest("/crops/gemini-advice/", {
                method: "POST",
                body: JSON.stringify(payload),
            });

            if (ai.ok && ai.data?.guidance) {
                incrementAiInsights();
                output.textContent = `${ai.data.guidance.text}\n\n[${ai.data.guidance.provider} · ${ai.data.guidance.model}] ${ai.data.guidance.disclaimer}`;
                copyBtn.classList.remove("d-none");
            } else {
                output.textContent = ai.data?.detail || "Gemini unavailable; the recommendations above still work.";
            }

            button.textContent = originalLabel;
            button.disabled = false;
        });

        advicePanel.append(btnGroup, output);
    }

    const aiTag = reply.data.ai_powered ? "✦ AI-Recommended" : "Fallback Mode";
    const locLabel = reply.data.analysis.location ? `, ${reply.data.analysis.location}` : "";
    message.className = "alert alert-success rounded-4 border-success-subtle";
    message.textContent = `${aiTag} for soil analysis #${reply.data.analysis.id} (${reply.data.analysis.soil_type || "soil"}, pH ${reply.data.analysis.soil_ph ?? "—"}${locLabel}) · ${reply.data.method}`;

    if (!isCare) {
        for (const crop of reply.data.recommendations) {
            const col = document.createElement("div");
            col.className = "col-md-6 col-lg-4";

            const card = document.createElement("article");
            card.className = "agr-crop-card h-100 p-4 d-flex flex-column";

            const topRow = document.createElement("div");
            topRow.className = "d-flex justify-content-between align-items-start mb-3";

            const icon = document.createElement("div");
            icon.className = "display-5";
            icon.textContent = crop.icon;

            const score = document.createElement("span");
            score.className = "agr-score-pill";
            score.textContent = crop.score === null ? "Insufficient data" : `${crop.score}/100 match`;

            topRow.append(icon, score);

            const title = document.createElement("h2");
            title.className = "h4 fw-bold text-dark";
            title.textContent = crop.name;

            const meta = document.createElement("p");
            meta.className = "small text-muted mb-2";
            meta.textContent = `Water: ${crop.water} · Temp: ${crop.temperature} · ${crop.duration}`;

            const reason = document.createElement("p");
            reason.className = "text-secondary small flex-grow-1";
            reason.textContent = crop.reasons.join("; ") || "More soil details required.";

            const link = document.createElement("a");
            link.className = "btn btn-outline-success fw-semibold mt-2";
            link.textContent = "View Care Plan →";
            link.href = `crop-care.html?soil_id=${encodeURIComponent(reply.data.analysis.id)}&crop=${encodeURIComponent(crop.name)}`;

            card.append(topRow, title, meta, reason, link);
            col.append(card);
            target.append(col);
        }
    } else {
        const plan = reply.data.care_plan;
        if (!plan) return;

        const header = document.createElement("h2");
        header.className = "h4 fw-bold text-dark col-12 mb-0";
        header.textContent = `${plan.crop} — Typical growing duration: ${plan.duration}`;
        target.append(header);

        for (const [title, key, icon] of [
            ["Fertilizer & Soil Testing", "fertilizer", "🌱"],
            ["Water & Irrigation", "irrigation", "💧"],
            ["Temperature", "temperature", "🌡️"],
            ["Plant Protection", "protection", "🛡️"],
        ]) {
            const col = document.createElement("div");
            col.className = "col-md-6";

            const card = document.createElement("article");
            card.className = "agr-crop-card h-100 p-4";

            const heading = document.createElement("h3");
            heading.className = "h5 fw-bold text-dark mb-2";
            heading.textContent = `${icon} ${title}`;

            const para = document.createElement("p");
            para.className = "text-secondary mb-0";
            para.textContent = plan[key];

            card.append(heading, para);
            col.append(card);
            target.append(col);
        }
    }
});