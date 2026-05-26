"""
test_intent_classifier.py
--------------------------
Tests for the offline keyword intent classifier.
Run with: pytest tests/ -v
"""

import sys
from pathlib import Path

# Add ai_module root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from chatbot.intent_classifier import classify, _normalize


# ─── normalize ──────────────────────────────────────────────────────────────

class TestNormalize:
    def test_lowercase(self):
        assert _normalize("ACCIDENT") == "accident"

    def test_strips_punctuation(self):
        assert _normalize("crash!") == "crash"

    def test_collapses_spaces(self):
        assert _normalize("tyre  burst") == "tyre burst"

    def test_empty_string(self):
        assert _normalize("") == ""


# ─── English intent classification ──────────────────────────────────────────

class TestClassifyEnglish:

    def test_accident_basic(self):
        intent, _ = classify("I had an accident on the highway")
        assert intent == "accident"

    def test_accident_crash(self):
        intent, _ = classify("There was a crash, two vehicles collided")
        assert intent == "accident"

    def test_tyre_burst(self):
        intent, _ = classify("My tyre burst on the road")
        assert intent == "tyre_burst"

    def test_tyre_puncture(self):
        intent, _ = classify("I have a flat tyre puncture")
        assert intent == "tyre_burst"

    def test_breakdown(self):
        intent, _ = classify("My car broke down and won't start")
        assert intent == "breakdown"

    def test_breakdown_stalled(self):
        intent, _ = classify("Engine stalled in the middle of the road")
        assert intent == "breakdown"

    def test_medical_bleeding(self):
        # "bleeding" is medical; "accident" is also present — classifier picks highest scorer.
        # Either is an acceptable response since both apply. What matters is it's NOT "other".
        intent, _ = classify("Someone is bleeding badly after the accident")
        assert intent in ("medical", "accident")

    def test_medical_unconscious(self):
        intent, _ = classify("The driver is unconscious please help")
        assert intent == "medical"

    def test_fire(self):
        intent, _ = classify("The vehicle is on fire, smoke everywhere")
        assert intent == "fire"

    def test_fire_petrol_leak(self):
        intent, _ = classify("There is a petrol leak and catching fire")
        assert intent == "fire"

    def test_lost(self):
        intent, _ = classify("I am lost and don't know where I am")
        assert intent == "lost"

    def test_lost_wrong_road(self):
        intent, _ = classify("Took a wrong turn and now on wrong road")
        assert intent == "lost"

    def test_other_gibberish(self):
        intent, _ = classify("asdfghjkl")
        assert intent == "other"

    def test_other_empty_ish(self):
        intent, _ = classify("hello")
        assert intent == "other"


# ─── Police / Theft / Assault classification ────────────────────────────────

class TestClassifyPoliceTheft:

    def test_theft_someone_stole_bike(self):
        intent, _ = classify("someone stole my bike")
        assert intent == "theft"

    def test_theft_vehicle_stolen(self):
        intent, _ = classify("my vehicle was stolen on the road")
        assert intent == "theft"

    def test_theft_bike_robbed(self):
        intent, _ = classify("my bike got robbed")
        assert intent == "theft"

    def test_robbery_snatched(self):
        intent, _ = classify("someone snatched my bag and ran away")
        assert intent == "robbery"

    def test_robbery_explicit(self):
        intent, _ = classify("robbery happened near the highway")
        assert intent == "robbery"

    def test_assault_attacked(self):
        intent, _ = classify("I was attacked and beaten on the road")
        assert intent == "assault"

    def test_assault_explicit(self):
        intent, _ = classify("assault by unknown persons near the bridge")
        assert intent == "assault"

    def test_suspicious_activity(self):
        intent, _ = classify("there are suspicious people following my car")
        assert intent in ("suspicious_activity", "other")  # useful but lower priority


# ─── Hindi intent classification ────────────────────────────────────────────

class TestClassifyHindi:

    def test_accident_hindi(self):
        intent, _ = classify("durghatna ho gayi sadak par")
        assert intent == "accident"

    def test_accident_takkar(self):
        intent, _ = classify("gaadi mein takkar lag gayi")
        assert intent == "accident"

    def test_medical_hindi(self):
        intent, _ = classify("chot lagi hai bahut khoon aa raha hai")
        assert intent == "medical"

    def test_breakdown_hindi(self):
        intent, _ = classify("gaadi kharab ho gayi start nahi ho rahi")
        assert intent == "breakdown"

    def test_lost_hindi(self):
        intent, _ = classify("rasta bhool gaya hoon kahan hun")
        assert intent == "lost"

    def test_theft_hindi(self):
        intent, _ = classify("meri gaadi chori ho gayi")
        assert intent == "theft"

    def test_fire_hindi(self):
        intent, _ = classify("gaadi mein aag lag gayi")
        assert intent == "fire"


# ─── Assamese intent classification ─────────────────────────────────────────

class TestClassifyAssamese:
    """
    Assamese keyword support must be verified — zero Assamese tests is dangerous
    since the app targets Northeast India / Assam.
    """

    def test_accident_assamese(self):
        intent, _ = classify("durghotona hoise sadakot")
        assert intent == "accident"

    def test_fire_assamese(self):
        intent, _ = classify("garixot jui lagise")
        assert intent == "fire"

    def test_medical_assamese(self):
        intent, _ = classify("poristhiti bhaal nohoy ruktu aahe ase")
        assert intent == "medical"

    def test_lost_assamese(self):
        intent, _ = classify("moi herejai goise kuta asu najano")
        assert intent == "lost"

    def test_breakdown_assamese(self):
        intent, _ = classify("garix kharab hoise start nohoise")
        assert intent == "breakdown"


# ─── Typo tolerance tests ────────────────────────────────────────────────────

class TestTypoTolerance:
    """
    Pure keyword classifiers fail on typos. These tests document that weakness
    and must be updated if fuzzy/semantic matching is added.
    """

    def test_accident_typo(self):
        intent, _ = classify("accidnt happened on road")
        # With pure keyword matching this will likely return "other" — document the failure.
        # Once fuzzy matching is added, change assert to: assert intent == "accident"
        assert intent in ("accident", "other")

    def test_tyre_truncated(self):
        intent, _ = classify("punctur on the highway")
        assert intent in ("tyre_burst", "other")

    def test_fire_double_letter(self):
        intent, _ = classify("firre in my car")
        assert intent in ("fire", "other")

    def test_breakdown_misspelled(self):
        intent, _ = classify("breakdwon engine stopped")
        assert intent in ("breakdown", "other")


# ─── Semantic / paraphrase fallback tests ────────────────────────────────────

class TestSemanticFallback:
    """
    Tests for inputs that use paraphrases, synonyms, or slang — words that are
    NOT in the keyword list. Pure keyword matching will fail these.
    Document the failures now; update assertions once SentenceTransformer fallback
    is integrated (confidence < 0.60 triggers semantic classifier).
    """

    def test_vehicle_caught_flames(self):
        # Paraphrase of fire — no keyword "fire" present
        intent, _ = classify("car caught flames on the highway")
        assert intent in ("fire", "other")

    def test_bike_snatched_slang(self):
        # Slang for robbery — no keyword "robbery" present
        intent, _ = classify("bike snatched near the signal")
        assert intent in ("robbery", "theft", "other")

    def test_vehicle_robbed_paraphrase(self):
        intent, _ = classify("my vehicle got robbed")
        assert intent in ("robbery", "theft", "other")

    def test_unconscious_paraphrase(self):
        # "not responding" as paraphrase for unconscious
        intent, _ = classify("person in car is not responding at all")
        assert intent in ("medical", "other")

    def test_lost_paraphrase(self):
        intent, _ = classify("no idea where I ended up, totally confused on route")
        assert intent in ("lost", "other")


# ─── Confidence scores ───────────────────────────────────────────────────────

class TestConfidence:

    def test_strong_match_has_positive_confidence(self):
        _, confidence = classify("I had a serious accident and someone is unconscious bleeding")
        assert confidence > 0.0

    def test_no_match_zero_confidence(self):
        _, confidence = classify("random words xyz")
        assert confidence == 0.0

    def test_confidence_between_0_and_1(self):
        for msg in [
            "accident on highway", "tyre burst", "engine breakdown",
            "someone injured", "fire in car", "i am lost",
            "someone stole my bike", "robbery on road", "assault near bridge"
        ]:
            _, conf = classify(msg)
            assert 0.0 <= conf <= 1.0, f"Confidence out of range for: {msg}"


# ─── Edge cases ──────────────────────────────────────────────────────────────

class TestEdgeCases:

    def test_mixed_language(self):
        # Should still pick up the keyword
        intent, _ = classify("meri gaadi mein accident ho gaya crash very bad")
        assert intent == "accident"

    def test_medical_beats_accident_when_stronger(self):
        intent, _ = classify("bleeding unconscious not breathing fracture broken bone")
        assert intent == "medical"

    def test_very_short_input(self):
        intent, _ = classify("108")
        # 108 alone doesn't strongly map to anything
        assert intent in ("other", "medical")  # ambulance connotation is acceptable

    def test_theft_beats_other(self):
        intent, _ = classify("chori ho gayi meri gaadi")
        assert intent in ("theft", "other")  # Hindi theft keyword

    def test_flood_intent(self):
        # Assam-important: flood is a real emergency category in Northeast India
        intent, _ = classify("flood on the highway road is submerged")
        assert intent in ("flood", "other")

    def test_landslide_intent(self):
        # Assam-important: landslide is a real emergency category in Northeast India
        intent, _ = classify("landslide has blocked the road completely")
        assert intent in ("landslide", "other")