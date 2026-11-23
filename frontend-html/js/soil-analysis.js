document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("soil-analysis-form");
    const successMessage = document.getElementById("success-message");
    const errorMessage = document.getElementById("error-message");
    const submitButton = document.getElementById("soil-submit-button");
    const submitText = document.getElementById("soil-submit-text");
    const submitSpinner = document.getElementById("soil-submit-spinner");
    const imageInput = document.getElementById("soil-image");
    const previewWrap = document.getElementById("soil-image-preview-wrap");
    const previewImg = document.getElementById("soil-image-preview");

    const PRESETS = {
        paddy: { ph: "6.4", moisture: "62", n: "48", p: "28", k: "40", type: "loamy", location: "Howrah, West Bengal" },
        vegetable: { ph: "6.5", moisture: "48", n: "42", p: "34", k: "38", type: "sandy", location: "Kolkata, West Bengal" },
        maize: { ph: "6.8", moisture: "52", n: "55", p: "30", k: "45", type: "black", location: "Pune, Maharashtra" },
    };

    document.querySelectorAll("[data-preset]").forEach((btn) => {
        btn.addEventListener("click", () => {
            const p = PRESETS[btn.getAttribute("data-preset")];
            if (!p) return;
            document.getElementById("soil-ph").value = p.ph;
            document.getElementById("moisture").value = p.moisture;
            document.getElementById("nitrogen").value = p.n;
            document.getElementById("phosphorus").value = p.p;
            document.getElementById("potassium").value = p.k;
            document.getElementById("soil-type").value = p.type;
            document.getElementById("location").value = p.location;
        });
    });

    if (imageInput && previewWrap && previewImg) {
        imageInput.addEventListener("change", function () {
            const file = imageInput.files && imageInput.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    previewImg.src = e.target.result;
                    previewWrap.classList.remove("d-none");
                };
                reader.readAsDataURL(file);
            } else {
                previewImg.src = "";
                previewWrap.classList.add("d-none");
            }
        });
    }

    function showSuccess(message) {
        successMessage.textContent = message;
        successMessage.classList.remove("d-none");
        errorMessage.classList.add("d-none");
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove("d-none");
        successMessage.classList.add("d-none");
    }

    function setLoading(loading) {
        submitButton.disabled = loading;
        if (loading) {
            submitText.textContent = "Saving Soil Analysis...";
            submitSpinner.classList.remove("d-none");
        } else {
            submitText.textContent = "Analyze Soil";
            submitSpinner.classList.add("d-none");
        }
    }

    function resetForm() {
        document.getElementById("soil-ph").value = "";
        document.getElementById("moisture").value = "";
        document.getElementById("nitrogen").value = "";
        document.getElementById("phosphorus").value = "";
        document.getElementById("potassium").value = "";
        document.getElementById("soil-type").value = "loamy";
        document.getElementById("location").value = "";
        if (imageInput) imageInput.value = "";
        if (previewWrap) previewWrap.classList.add("d-none");
        if (previewImg) previewImg.src = "";
    }

    function incrementAiInsights() {
        const current = parseInt(localStorage.getItem("agrivision_ai_insights_count") || "0", 10);
        localStorage.setItem("agrivision_ai_insights_count", String((Number.isFinite(current) ? current : 0) + 1));
    }

    form.addEventListener("submit", async function (event) {
        event.preventDefault();
        setLoading(true);
        successMessage.classList.add("d-none");
        errorMessage.classList.add("d-none");

        try {
            const data = new FormData();
            data.append("soil_ph", document.getElementById("soil-ph").value);
            data.append("moisture", document.getElementById("moisture").value);
            data.append("nitrogen", document.getElementById("nitrogen").value);
            data.append("phosphorus", document.getElementById("phosphorus").value);
            data.append("potassium", document.getElementById("potassium").value);
            data.append("soil_type", document.getElementById("soil-type").value);
            data.append("location", document.getElementById("location").value);
            if (imageInput && imageInput.files && imageInput.files[0]) {
                data.append("soil_image", imageInput.files[0]);
            }

            const response = await apiRequest("/soil/", {
                method: "POST",
                body: data,
            });

            if (!response.ok) {
                let errorText = "Failed to save soil analysis.";
                if (response.data && typeof response.data === "object") {
                    const details = Object.entries(response.data)
                        .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`)
                        .join(" · ");
                    if (details) errorText += ` ${details}`;
                }
                showError(errorText);
                return;
            }

            const assessment = response.data.assessment || {};
            const summary = [
                assessment.acidity && `pH: ${assessment.acidity}`,
                assessment.moisture_status && `Moisture: ${assessment.moisture_status}`,
                ...(assessment.notes || []),
            ].filter(Boolean).join(" · ");

            showSuccess(`Saved! ${summary}`);

            const result = document.getElementById("soil-result");
            if (result) {
                result.replaceChildren();

                const headerRow = document.createElement("div");
                headerRow.className = "d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3";

                const title = document.createElement("h3");
                title.className = "h5 fw-bold text-dark mb-0";
                title.textContent = "Preliminary Soil Screening";

                const badge = document.createElement("span");
                badge.className = "agr-ai-badge-pill";
                badge.textContent = "Saved to Workspace";

                headerRow.append(title, badge);

                // Visual pH & Moisture Gauges
                const gauges = document.createElement("div");
                gauges.className = "row g-3 mb-3 p-3 rounded-3 bg-white border";

                const phVal = response.data.soil_ph;
                const phPct = phVal != null ? Math.max(0, Math.min(100, (Number(phVal) / 14) * 100)) : 50;
                const mVal = response.data.moisture;
                const mPct = mVal != null ? Math.max(0, Math.min(100, Number(mVal))) : 0;

                gauges.innerHTML = `
                    <div class="col-md-6">
                        <div class="d-flex justify-content-between small fw-semibold mb-1">
                            <span>Soil pH Scale (0–14)</span>
                            <span class="text-success">${phVal ?? "—"} (${assessment.acidity || ""})</span>
                        </div>
                        <div class="agr-ph-scale"><div class="agr-ph-marker" style="left: ${phPct}%;"></div></div>
                    </div>
                    <div class="col-md-6">
                        <div class="d-flex justify-content-between small fw-semibold mb-1">
                            <span>Moisture Level</span>
                            <span class="text-primary">${mVal ?? "—"}%</span>
                        </div>
                        <div class="progress" style="height: 10px; border-radius: 999px;">
                            <div class="progress-bar bg-success" style="width: ${mPct}%;"></div>
                        </div>
                    </div>
                `;

                const text = document.createElement("p");
                text.className = "text-secondary small mb-3";
                text.textContent = summary + (assessment.disclaimer ? ` — ${assessment.disclaimer}` : "");

                const btnRow = document.createElement("div");
                btnRow.className = "d-flex flex-wrap gap-2";

                const link = document.createElement("a");
                link.href = `crop-recommendation.html?soil_id=${encodeURIComponent(response.data.id)}`;
                link.textContent = "View Crop Recommendations →";
                link.className = "btn btn-success fw-semibold";

                const aiButton = document.createElement("button");
                aiButton.type = "button";
                aiButton.className = "btn btn-outline-success fw-semibold";
                aiButton.textContent = "✦ Explain Soil with Gemini AI";

                const copyBtn = document.createElement("button");
                copyBtn.type = "button";
                copyBtn.className = "btn btn-light border fw-semibold d-none";
                copyBtn.textContent = "Copy Advice";

                btnRow.append(link, aiButton, copyBtn);

                const aiText = document.createElement("div");
                aiText.className = "agr-ai-output-box mt-3 d-none";
                aiText.setAttribute("aria-live", "polite");

                copyBtn.addEventListener("click", async () => {
                    if (!aiText.textContent) return;
                    await navigator.clipboard.writeText(aiText.textContent);
                    copyBtn.textContent = "Copied!";
                    setTimeout(() => { copyBtn.textContent = "Copy Advice"; }, 1800);
                });

                aiButton.addEventListener("click", async () => {
                    aiButton.disabled = true;
                    aiButton.textContent = "Generating Gemini guidance…";
                    aiText.classList.remove("d-none");
                    aiText.textContent = "Asking Google Gemini for educational soil guidance…";

                    const ai = await apiRequest("/crops/gemini-advice/", {
                        method: "POST",
                        body: JSON.stringify({ soil_id: response.data.id, topic: "soil" }),
                    });

                    if (ai.ok && ai.data?.guidance) {
                        incrementAiInsights();
                        aiText.textContent = `${ai.data.guidance.text}\n\n[${ai.data.guidance.provider} · ${ai.data.guidance.model}] ${ai.data.guidance.disclaimer}`;
                        copyBtn.classList.remove("d-none");
                    } else {
                        aiText.textContent = ai.data?.detail || "Gemini service unavailable; preliminary results remain available.";
                    }

                    aiButton.textContent = "✦ Explain Soil with Gemini AI";
                    aiButton.disabled = false;
                });

                result.append(headerRow, gauges, text, btnRow, aiText);
                result.classList.remove("d-none");
            }

            resetForm();
        } catch (error) {
            console.error(error);
            showError("Unable to connect to the Agrivision backend.");
        } finally {
            setLoading(false);
        }
    });
});