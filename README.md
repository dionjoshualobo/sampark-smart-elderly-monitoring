# SAMPARK - AI-Based Elderly Care System

SAMPARK is an elderly care prototype that combines wearable-style health data, conversational input, machine learning risk prediction, alerts, and a dashboard with integrated voice assistant.

## 🚀 Quick Start (One Command)

```bash
pip install -r requirements.txt
python run_sampark.py
```

That's it. The launcher starts everything in one process:

| What | Where |
| --- | --- |
| Backend API | http://127.0.0.1:5000 |
| **Care Dashboard** (auto-opens in browser) | http://127.0.0.1:5000/dashboard |
| **Watch Simulator** (live watch UI) | http://127.0.0.1:5000/watch |
| Phone Voice page | http://127.0.0.1:5000/phone |

A background watch feed also streams simulated vitals every 10 seconds so the dashboard has live data immediately.

Press `Ctrl+C` to stop everything.

### Launcher Options

```bash
python run_sampark.py --no-watch          # no background data feed
python run_sampark.py --mode warning      # feed generates risky vitals (triggers alerts)
python run_sampark.py --interval 5        # watch reading every 5s
python run_sampark.py --port 5050         # custom backend port
python run_sampark.py --no-browser        # do not auto-open the dashboard
python run_sampark.py --reset-db          # wipe saved records and alerts first
python run_sampark.py --streamlit         # also start the optional Streamlit dashboard
```

If dependencies are missing, the launcher tries to install them automatically.

## ⌚ Watch Simulation & Alert System

The system simulates a real smartwatch (Mi Band / Google Fit style) end to end:

### Watch Simulator (`/watch`)
- Live watch face with animated heart pulse that beats at the current heart rate.
- Real-time vitals: heart rate, SpO2, steps (with natural rest cycles), sleep hours.
- Scrolling ECG-style signal trace.
- Modes: **Normal**, **Warning** (risky vitals), **Random Mix**.
- Auto-send toggle with adjustable interval, plus a manual **Send Now** button.
- **Fall Detected** button sends a one-shot fall emergency.

### How Alerts Fire
When any health record arrives (from the watch, voice assistant, or API), the backend evaluates it and creates caregiver alerts:

| Condition | Severity |
| --- | --- |
| High ML/rule risk | High |
| Fall reported | High |
| SpO2 below 94% | High |
| Heart rate < 55 or > 110 bpm | Medium |
| Missed medicine | Medium |

High-risk alerts also trigger a caretaker email when Gmail credentials are configured (otherwise they are simulated).

The dashboard shows new high-severity alerts with a red toast notification and an audible beep, and each alert can be **acknowledged** by the caregiver.

Duplicate alerts are suppressed by a 60-second cooldown per alert type (configurable via the `SAMPARK_ALERT_COOLDOWN` environment variable). Emergency alerts always bypass the cooldown.

## 💬 Voice & Chat Assistant

Open the assistant widget on the dashboard (bottom-right 💬 button):
- **Text chat**: type messages such as "I slept 6 hours and took my medicine".
- **Voice recognition**: speak naturally (Chrome recommended).
- **Emergency button**: one-click caregiver alert.
- The phone page (`/phone`) gives a mobile-friendly voice interface on your phone.
- Optional LLM mode for human-like replies:

```bash
export GEMINI_API_KEY="your_key"     # or OPENAI_API_KEY
export SAMPARK_USE_LLM=1
```

## System Architecture

```text
Wearable / Watch Data            Voice Input
        |                            |
Wearable Simulator (/watch)   Dashboard Chat / Phone Voice
        |                            |
        +--------> Flask Backend + SQLite + Random Forest <-+
                             |
              Risk Prediction -> Alerts -> Email
                             |
                Dashboard (real-time view)
```

## Project Parts

```text
backend/
  Flask API, SQLite database, Random Forest training,
  risk engine, alert engine, email notifier, assistant endpoint

wearable_simulator/
  simulator.py       background Python data feed
  watch.html         visual watch simulator page served at /watch

dashboard/
  index.html         main care dashboard served at /dashboard
  app.py             optional Streamlit dashboard

phone_voice/
  index.html         mobile voice page served at /phone

voice_assistant/
  Text/microphone assistants (optional PC tools)

demo_cases.json
  Sample Low, Medium, and High risk test cases
```

## Main Data Format

```json
{
  "heart_rate": 80,
  "spo2": 97,
  "steps": 4000,
  "sleep_hours": 4,
  "missed_meds": 1,
  "missed_meals": 0,
  "falls": 0
}
```

Missing fields are filled with defaults or carried forward from the last record, so partial watch payloads are accepted.

## Running Parts Separately (Optional)

You rarely need this — `run_sampark.py` covers it all — but each part runs standalone:

```bash
# Backend only
python backend/app.py

# Streamlit dashboard (needs requirements-full.txt)
pip install -r requirements-full.txt
streamlit run dashboard/app.py

# Background Python watch feed
python wearable_simulator/simulator.py --live [--mode warning] [--interval 5]

# PC text / microphone assistant
python voice_assistant/assistant.py
python voice_assistant/voice_mode.py
```

## ML Model

Random Forest classifier trained on synthetic health data.

```bash
cd backend
python train_model.py    # regenerates sampark_model.pkl
```

A pre-trained model ships with the repo; if it is missing, the backend falls back to rule-based scoring automatically.

## API Endpoints

```text
GET  /                          API info + page links
GET  /dashboard                 Care dashboard page
GET  /watch                     Watch simulator page
GET  /phone                     Phone voice page
POST /health-data               Save health record (auto risk + alerts)
GET  /health-data               List records
GET  /health-data/latest        Latest record
GET  /health-data/<id>          Specific record
GET  /alerts                    List alerts
GET  /alerts/latest             Latest alert
POST /alerts/<id>/acknowledge   Acknowledge an alert
POST /emergency                 Emergency alert (bypasses cooldown)
GET  /email-status              Gmail configuration status
POST /assistant-message         Conversational assistant
POST /predict                   Predict risk without saving
```

## Gmail Alerts (Optional)

```bash
export SAMPARK_GMAIL_ADDRESS="you@gmail.com"
export SAMPARK_GMAIL_APP_PASSWORD="your_app_password"
export SAMPARK_CARETAKER_EMAIL="caretaker@gmail.com"
```

Without these, emails are simulated and marked as such in the alert log.

## Demo Flow

1. Run `python run_sampark.py` — dashboard opens automatically.
2. Open `/watch` in another tab; press **Send Now** and see the record arrive.
3. Switch the watch to **Warning** mode or press **Fall Detected**.
4. Watch the dashboard fire a red toast + sound alert within seconds.
5. Acknowledge the alert as the caregiver.
6. Use the chat widget: "I did not take medicine and slept only 4 hours".

## Viva Explanation

SAMPARK is built as a modular system. The wearable side streams physical parameters such as heart rate, SpO2, steps, and sleep through the watch simulator (replaceable later by Google Fit). The voice assistant collects behavioral data such as missed medicine, meals, sleep, and falls. The Flask backend merges these values, stores them in SQLite, and predicts health risk using a Random Forest model combined with rule checks. The alert engine turns risky readings into prioritized caregiver alerts with email escalation, cooldown-based deduplication, and acknowledgment tracking, while the dashboard displays everything in real time.
