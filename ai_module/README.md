# RoadSOS — AI Module

**Owner:** Alokesh (AI / ML Lead)  
**Stack:** Python 3.11 · FastAPI · SQLite · Google Gemini API  
**Version:** 1.0 | May 2026

---

## What this module does

1. **Online chatbot** — FastAPI server exposes `POST /chat`. Receives user message + GPS context from Android (via backend proxy), builds a context-aware system prompt, calls the Gemini API, returns a structured JSON response with intent + suggested actions.

2. **Offline intent classifier** — When there is no network, Android runs keyword matching locally against `chatbot_intents.json`. The same logic lives in `intent_classifier.py` so it can be tested server-side too.

3. **Offline SQLite database** — Pre-seeded district hospital, police station, and emergency number data for Assam and NE India. Compiled from CSV files by `build_db.py` and shipped inside the Android APK.

---

## Folder structure

```
ai_module/
├── chatbot/
│   ├── api.py                  ← FastAPI server (entry point)
│   ├── prompt_engine.py        ← builds system prompt from context
│   ├── intent_classifier.py    ← offline keyword → intent matcher
│   └── response_templates.py  ← scripted offline responses
├── offline_database/
│   ├── schema.sql              ← SQLite schema (share with Android dev)
│   ├── build_db.py             ← CSV → SQLite + JSON compiler
│   └── data/
│       ├── hospitals.csv
│       ├── police_stations.csv
│       ├── emergency_numbers.csv
│       ├── nh_corridors.csv
│       └── chatbot_intents.json
├── tests/
│   ├── test_intent_classifier.py
│   └── test_api_contract.py
├── .env.example
├── requirements.txt
└── README.md
```

---

## Setup

```bash
# 1. Clone repo and navigate here
cd ai_module

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 5. Build the offline database
python offline_database/build_db.py

# 6. Run the API server
uvicorn chatbot.api:app --reload --port 8000
```

---

## API

`POST /chat` — see `chatbot/api.py` for full request/response schema.

`GET /health` — returns `{"status": "ok"}`.

---

## Running tests

```bash
pytest tests/ -v
```

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Google Gemini API key |
| `DB_PATH` | No | Path to SQLite DB (default: `offline_database/roadsos.db`) |
| `MAX_HISTORY_TURNS` | No | Max chat history turns to send to LLM (default: 6) |
| `LLM_TIMEOUT_SECONDS` | No | LLM call timeout before offline fallback (default: 4) |

---

## Integration notes for backend dev

- Deploy this FastAPI app (e.g. on Cloud Run or Railway).
- Point `chatProxy.js` to this server's URL.
- The backend adds the `Authorization: Bearer <GEMINI_API_KEY>` header — this key must NEVER go to Android.
- Every response includes a `source` field: `"llm"` or `"offline_template"` so Android knows which path was used.
