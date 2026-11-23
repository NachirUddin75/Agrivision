# Agrivision — Gemini-powered educational farming project

This is the complete **Django REST + HTML/CSS/JavaScript/Vite** project. It includes account creation, email verification, soil measurements, a user-specific dashboard, 6 rule-based crop candidates, crop-care/irrigation guidance and an **Open-Meteo current weather + 7-day forecast page** with weather-aware irrigation guidance (no weather API key), plus **optional Gemini AI text explanations** for soil, crop selection, crop care and weather-aware irrigation.

**Removed/not included:** AI Farmer Chatbot and Plant Disease Detection from Images. There is no disease diagnostic endpoint, chatbot endpoint, or upload control for those features. Gemini does **not** process images here. Crop scores are illustrative rules, **not** trained ML or yield predictions. Agrivision retrieves modeled weather forecasts from Open-Meteo, not live on-field weather or soil sensor readings.

## Requirements for a Windows PC

- Python **3.12 or 3.13** installed with `py` launcher and pip (other compatible versions may work).
- Node.js **22+** and npm.
- Internet access for the first dependency installation and for live Gemini calls and Open-Meteo weather requests.
- A Google Gemini API key if you want Gemini-generated text: https://aistudio.google.com/apikey . Gemini usage is subject to provider quotas/charges.

## Quick setup

1. Extract the complete ZIP. Open PowerShell **inside the `Agrivision` directory** (same folder as this README).
2. Run `powershell -ExecutionPolicy Bypass -File .\SETUP_WINDOWS.ps1`. This creates a Python virtual environment, installs Python/Node dependencies, initializes SQLite, and creates `backend/.env` if missing. It **does not overwrite** an existing `.env`.
3. Edit **`backend/.env`**. Replace `GEMINI_API_KEY=PASTE_YOUR_GEMINI_API_KEY_HERE` with your own key. `GEMINI_MODEL=gemini-2.5-flash` can be updated to a model your API key can access. **Never share/commit `.env`.**
4. Run `START_AGRIVISION.bat` to open the backend and frontend terminals. Then open http://localhost:5173 (and http://127.0.0.1:8000/admin/ for Django admin if you create a superuser).
5. Register from the frontend. With no `BREVO_API_KEY`, email verification and login OTP instructions **appear in the Django terminal in local DEBUG mode only**. Copy the **full verification link** from that terminal into a browser to activate the new account; then log in. For production, configure a real mail provider.
6. Complete a soil form. Open Crop Recommendations, choose a crop and its Crop Care page. Press **Generate Gemini ...** to call Gemini. Open **Weather & Irrigation** from the dashboard, enter your town, view the forecast and optional Gemini weather-based irrigation advice. The basic results continue to work even if Gemini is unavailable.

**For manual start:** In terminal 1, `cd backend`, `.\.venv\Scripts\python.exe manage.py runserver`; in terminal 2, `cd frontend-html`, `npm run dev`.

**Run tests:** `cd backend` then `.\.venv\Scripts\python.exe manage.py test soil crops` and `.\.venv\Scripts\python.exe manage.py check`.

## API endpoints (JWT Bearer token required)

| Method | Path | Purpose |
| --- | --- | --- |
| GET/POST | `/api/soil/` | List or create the signed-in user's soil readings with preliminary screening |
| GET | `/api/crops/recommendations/?soil_id=1&crop=Rice` | Rule-based scores and basic crop-care notes |
| POST | `/api/crops/gemini-advice/` | Gemini text advice for `topic=soil`, `crops`, `care` or `weather`; body also accepts `soil_id`, `crop` (for care), and `city` (for weather) |
| GET | `/api/crops/weather/?city=Howrah` | Current weather, seven-day forecast and weather-based irrigation note from Open-Meteo; no weather key required |
| POST | `/api/accounts/token/refresh/` | Renew JWT access token |

Weather is available without a Gemini key, but needs internet. Weather-city geocoding may match ambiguous place names; confirm the location shown. Open-Meteo free access has non-commercial conditions and usage limits. The weather route caches results for 10 minutes. Weather AI also needs an existing soil analysis.

A sample Gemini request body is `{ "topic": "care", "soil_id": 1, "crop": "Rice" }`. Gemini requests are only made when the user clicks the AI button, and the API key is **only used by Django**; the browser never receives it.

## Security and limitations

- Soil readings can only be fetched by their owner. Users cannot request another user's soil record for Gemini analysis.
- Do not send real private field measurements to Gemini without appropriate consent; soil readings are transmitted to Google when AI advice is requested. Optional free/paid quotas and data policies depend on the provider's terms.
- This is for **college demonstrations/education**; don't use AI text to choose pesticide dosage, fertilizer prescriptions, precise litres of irrigation or diagnose diseases.
- On localhost, SQLite is the default database, so there is **no database key to add**. Optional production PostgreSQL is controlled through `DATABASE_URL`. Old `.env` / DB files are not packaged.
- Local email console mode is **DEBUG=True only**. In production use `DEBUG=False`, real mail credentials, production database, TLS, secure hosts, proper static serving and a separate deployment review.
- External Gemini service operation was not verified without a real API key. If you get a key error, inspect the backend terminal and confirm the model is enabled for your key.
