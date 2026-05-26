"""
intent_classifier.py
--------------------
Offline keyword-based intent classifier.
Used when:
  1. There is no network (Android runs chatbot_intents.json locally)
  2. The LLM API call times out (server-side fallback)
  3. During testing

Algorithm:
  - Each intent has a list of keywords with optional weights.
  - The user message is lowercased and checked for each keyword.
  - The intent with the highest total score wins.
  - If no keywords match, returns "other".

Supports English, Hindi, and Assamese keywords.

FIXES APPLIED (2026-05):
  #1  Added missing intents: theft, robbery, assault,
      suspicious_activity, flood, landslide.
      These are real emergency categories in Northeast India and are
      already supported by the backend — the offline layer was lagging.

  KNOWN ARCHITECTURAL LIMITATION (not fixed here — tracked separately):
      This classifier is pure keyword matching. It fails on:
        - Typos ("accidnt", "punctur", "firre")
        - Paraphrases ("my bike got robbed", "someone snatched bike")
        - Slang and regional variants
      The planned fix is a hybrid pipeline:
        Step 1 → this classifier (fast, offline)
        Step 2 → SentenceTransformer semantic fallback if confidence < 0.60
      Tests for typos and paraphrases are in test_intent_classifier.py
      to document the known failure modes until the hybrid is in place.
"""

import json
import os
import re
from pathlib import Path


# ─── Intent keyword definitions ────────────────────────────────────────────
# Format: "keyword": weight  (higher weight = stronger signal)
# Words that are very specific to one intent get weight 2 or 3.
# Common words that might appear in multiple contexts get weight 1.

INTENT_KEYWORDS: dict[str, dict[str, float]] = {

    "accident": {
        # English
        "accident": 3, "crash": 3, "collision": 3, "collide": 2,
        "hit": 1, "smash": 2, "impact": 2, "vehicle hit": 3,
        "road accident": 3, "met with accident": 3, "car accident": 3,
        # Hindi
        "durghatna": 3, "takkar": 3, "hadsa": 3, "tohna": 2,
        # Assamese
        "durghotona": 3, "thapia": 2,
    },

    "tyre_burst": {
        # English
        "tyre": 2, "tire": 2, "flat tyre": 3, "flat tire": 3,
        "burst": 2, "puncture": 3, "blowout": 3, "wheel": 1,
        "tyre burst": 3, "tire burst": 3,
        # Hindi
        "tyre phata": 3, "puncture ho gaya": 3, "chakka phata": 3,
        # Assamese
        "tyre phakil": 3,
    },

    "breakdown": {
        # English
        "breakdown": 3, "broke down": 3, "broken down": 3,
        "engine": 1, "stalled": 3, "not starting": 3, "wont start": 3,
        "won't start": 3, "engine failure": 3, "car stopped": 2,
        "vehicle stopped": 2, "overheating": 2, "battery dead": 3,
        "no fuel": 2, "out of fuel": 3, "petrol finish": 3,
        # Hindi
        "gaadi kharab": 3, "engine band": 2, "start nahi": 3,
        # Assamese
        "gari bhal nai": 3,
    },

    "medical": {
        # English
        "injured": 2, "injury": 2, "bleeding": 3, "blood": 2,
        "unconscious": 3, "fainted": 3, "not breathing": 3,
        "heart attack": 3, "chest pain": 3, "ambulance": 2,
        "hospital": 1, "doctor": 1, "hurt": 2, "pain": 1,
        "fracture": 3, "broken bone": 3, "head injury": 3,
        # Hindi
        "chot lagi": 3, "khoon": 2, "behosh": 3, "ambulance chahiye": 3,
        # Assamese
        "aahat": 3, "hospital lagibo": 2,
    },

    "fire": {
        # English
        "fire": 3, "smoke": 2, "burning": 3, "flame": 3,
        "fuel leak": 3, "petrol leak": 3, "catching fire": 3,
        "on fire": 3, "vehicle fire": 3,
        # Hindi
        "aag": 3, "dhuan": 2, "jal raha": 3,
        # Assamese
        "জুই": 3,
    },

    "lost": {
        # English
        "lost": 2, "direction": 2, "where am i": 3, "wrong road": 2,
        "wrong turn": 2, "dont know where": 3, "don't know where": 3,
        "navigation": 1, "route": 1, "map": 1,
        # Hindi
        "rasta bhool gaya": 3, "kahan hun": 3, "rasta nahi pata": 3,
        # Assamese
        "baat haroilun": 3,
    },

    # ── NEW INTENTS ──────────────────────────────────────────────────────────

    "theft": {
        # English
        "stolen": 3, "stole": 3, "theft": 3, "robbed": 3,
        "snatched": 3, "snatch": 2, "pickpocket": 3, "vehicle stolen": 3,
        "bike stolen": 3, "car stolen": 3, "chain snatching": 3,
        "my bike": 1, "took my": 2,
        # Hindi
        "chori": 3, "churaya": 3, "loot liya": 3, "gaadi chori": 3,
        # Assamese
        "churi": 3, "luta": 2,
    },

    "robbery": {
        # English
        "robbery": 3, "robber": 3, "armed robbery": 3, "gunpoint": 3,
        "knifepoint": 3, "looted": 3, "loot": 2, "mugged": 3,
        "mugging": 3, "dacoit": 3, "dacoity": 3, "highway robbery": 3,
        # Hindi
        "dakaiti": 3, "loot": 2, "luta": 3, "loota": 3,
        # Assamese
        "dakat": 3, "luta": 2,
    },

    "assault": {
        # English
        "attack": 2, "attacked": 3, "assault": 3, "assaulted": 3,
        "beat": 1, "beaten": 3, "fight": 2, "fighting": 2,
        "violence": 3, "mob": 2, "mob attack": 3, "hitting me": 3,
        "threatening": 2, "threat": 2,
        # Hindi
        "maar": 2, "maara": 3, "pitai": 3, "hamla": 3, "dhakka": 2,
        # Assamese
        "maar": 2, "aakroman": 3,
    },

    "suspicious_activity": {
        # English
        "suspicious": 3, "following me": 3, "being followed": 3,
        "someone following": 3, "unsafe": 2, "scared": 1,
        "strange vehicle": 2, "watching me": 2, "feels unsafe": 3,
        "danger": 1, "help me": 1,
        # Hindi
        "peeche aa raha": 3, "dar lag raha": 2, "koi peeche": 3,
        # Assamese
        "picha lisei": 3,
    },

    "flood": {
        # English
        "flood": 3, "flooded": 3, "flooding": 3, "waterlogged": 3,
        "water on road": 3, "road underwater": 3, "submerged": 3,
        "flash flood": 3, "river overflow": 3, "inundated": 3,
        # Hindi
        "baarh": 3, "paani bhar gaya": 3, "sadak doob gayi": 3,
        # Assamese
        "bon": 3, "baanya": 3, "pani bhari goise": 3,
    },

    "landslide": {
        # English
        "landslide": 3, "mudslide": 3, "rockfall": 3, "rockslide": 3,
        "road blocked": 2, "boulders": 2, "mud on road": 2,
        "hill collapse": 3, "slope collapse": 3,
        # Hindi
        "bhookamp": 1, "pahad khisak": 3, "mitti giri": 3,
        "pathar gira": 3,
        # Assamese
        "mati khasil": 3, "parbat dhosa": 3,
    },
}


def _normalize(text: str) -> str:
    """Lowercase, strip punctuation, collapse spaces."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def classify(user_message: str) -> tuple[str, float]:
    """
    Classify a user message into one of the defined intents.

    Returns:
        (intent: str, confidence: float)
        confidence is a normalised score 0.0–1.0
        intent is "other" if nothing matches above threshold.

    NOTE ON LIMITATIONS:
        Pure keyword matching. Known failure modes that tests document:
        - Typos: "accidnt", "punctur", "firre" → may return "other"
        - Paraphrases: "my bike got robbed" → may miss "theft"
        - Slang: regional variants not in the keyword list
        These are tested in test_intent_classifier.py as known failures
        until the SentenceTransformer hybrid fallback is integrated.
    """
    normalized = _normalize(user_message)
    scores: dict[str, float] = {intent: 0.0 for intent in INTENT_KEYWORDS}

    for intent, keywords in INTENT_KEYWORDS.items():
        for kw, weight in keywords.items():
            # Check whole-word or phrase match
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, normalized):
                scores[intent] += weight

    best_intent = max(scores, key=lambda k: scores[k])
    best_score = scores[best_intent]

    # Normalise: max possible score per intent varies, so use a simple threshold
    THRESHOLD = 1.0
    if best_score < THRESHOLD:
        return "other", 0.0

    # Rough confidence: cap at 1.0
    total = sum(scores.values()) or 1
    confidence = min(best_score / total, 1.0)

    return best_intent, round(confidence, 3)


def classify_from_json(
    user_message: str,
    intents_json_path: str | None = None,
) -> dict:
    """
    Classify using the chatbot_intents.json file as the source of truth.
    Falls back to the hardcoded INTENT_KEYWORDS if the file is not found.

    Returns a dict matching the /chat response shape for offline use.
    """
    from chatbot.response_templates import get_template

    # Try JSON-based classification first
    if intents_json_path is None:
        intents_json_path = str(
            Path(__file__).parent.parent / "offline_database" / "data" / "chatbot_intents.json"
        )

    intent, confidence = classify(user_message)

    # If JSON file exists, try to get the response text from there
    if os.path.exists(intents_json_path):
        try:
            with open(intents_json_path, encoding="utf-8") as f:
                intents_data = json.load(f)
            for item in intents_data:
                if item["intent"] == intent:
                    return {
                        "intent": intent,
                        "confidence": confidence,
                        "reply": item.get("response_en", ""),
                        "action_label": item.get("action_label", ""),
                        "action_number": item.get("action_number", "112"),
                        "extra_actions": item.get("extra_actions", []),
                        "source": "offline_json",
                    }
        except (json.JSONDecodeError, KeyError):
            pass  # fall through to Python templates

    # Fallback to hardcoded templates
    template = get_template(intent)
    return {
        "intent": intent,
        "confidence": confidence,
        "reply": template["reply"],
        "action_label": template["action_label"],
        "action_number": template["action_number"],
        "extra_actions": template["extra_actions"],
        "source": "offline_template",
    }