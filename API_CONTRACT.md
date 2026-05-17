# API Contract — RoadSoS AI/ML ↔ Backend Integration

**Owner:** Swapnil (AI/ML)  
**Integrating:** Alokesh (FastAPI backend)  
**Last updated:** May 17, 2026

---

## Endpoint: POST /chat

This is the only endpoint the AI/ML layer touches. Implement this pattern exactly in your FastAPI route.

---

## Imports (add to your route file)

```python
from utils.classifier import classify_emergency, detect_severity
from ranking.scorer import score_facilities, to_api_response, get_weights
from chatbot.chain import get_chat_response
```

---

## Full Integration Pattern

```python
@app.post("/chat")
async def chat(request: ChatRequest):

    # Step 1 — Fake/prank detection
    classification = classify_emergency(request.message)

    if not classification["proceed"]:
        return get_canned_test_response()

    # Step 2 — Auto-detect severity from message (no manual input needed)
    severity = detect_severity(request.message)
    weights = get_weights(severity)

    # Step 3 — Score and rank facilities
    scored = score_facilities(
        raw_db_rows,          # your DB query result
        request.lat,
        request.lon,
        weights=weights
    )
    ranked = to_api_response(scored)

    # Step 4 — Get AI response
    reply = get_chat_response(
        message=request.message,
        lat=request.lat,
        lon=request.lon,
        nearby_facilities=ranked,
        severity=severity        # pass through so chatbot tone matches urgency
    )

    # Step 5 — Append warning if suspicious
    if classification["status"] == "SUSPICIOUS":
        reply += get_suspicious_warning()

    return {
        "facilities": ranked,
        "ai_response": reply,
        "severity_detected": severity    # expose for Android UI (e.g. red banner)
    }
```

---

## What Each Function Returns

### `classify_emergency(message: str)`
```python
{
    "status": "REAL" | "SUSPICIOUS" | "TEST",
    "confidence": float,       # 0.0 – 1.0
    "reason": str,
    "proceed": bool            # False only for TEST
}
```

### `detect_severity(message: str)`
```python
"serious" | "minor" | "default"
# No API call — instant keyword match
# serious → quality-weighted scoring (head trauma, cardiac, unconscious)
# minor   → distance-weighted scoring
# default → balanced weights
```

### `get_weights(severity: str)`
```python
# serious  → {"distance": 0.25, "rating": 0.45, "response_time": 0.20, "availability": 0.10}
# minor    → {"distance": 0.55, "rating": 0.15, "response_time": 0.20, "availability": 0.10}
# default  → {"distance": 0.40, "rating": 0.25, "response_time": 0.20, "availability": 0.15}
```

### `score_facilities(facilities, lat, lon, weights)`
- Input: raw DB rows (list of dicts), user coordinates, weight dict  
- Output: sorted list of scored facility dicts  
- **Waiting on Member 4's schema** — `_FIELD_MAP` in `scorer.py` will be updated once schema is confirmed. Do not hardcode column names on your side.

### `to_api_response(scored)`
- Flattens scored list into JSON-serializable format  
- Pass directly into `get_chat_response` as `nearby_facilities`

### `get_chat_response(message, lat, lon, nearby_facilities, severity)`
- Returns: `str` — the full AI response to show the user  
- `nearby_facilities=None` is allowed during dev/testing  

---

## What You Need to Pass In

| Parameter | Source |
|---|---|
| `request.message` | Android client |
| `request.lat`, `request.lon` | Android GPS |
| `raw_db_rows` | Your Supabase/SQLite query — all facilities within reasonable radius |

---

## Notes

- `severity_detected` in the response is for Android — they can use it to trigger UI changes (red alert banner for serious, etc.)
- Do not pass severity manually — `detect_severity()` handles it automatically
- `_FIELD_MAP` update pending Member 4's schema — scorer will break on wrong column names, so smoke test after schema lands