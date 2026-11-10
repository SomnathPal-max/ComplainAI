import pytest
from backend.ai.priority_engine import priority_engine, haversine_distance_meters
from backend.ai.multimodal_triage import multimodal_triage
from backend.ai.anti_fake_closure import anti_fake_guard
from backend.ai.zero_touch_resolver import zero_touch_resolver
from backend.ai.copilot import empathy_copilot
from backend.ai.clustering import swarm_clustering
from backend.database import db
from backend.config import settings

def test_haversine_distance():
    """Verify distance calculation between coordinates."""
    # St. Jude Hospital coords: 37.7833, -122.4167
    dist = haversine_distance_meters(37.7833, -122.4167, 37.7830, -122.4160)
    assert 0 < dist < 120  # less than 120 meters

def test_dynamic_priority_formula_with_vulnerability_boost():
    """
    Verify dynamic priority formula:
    P_score = (w1 * NLP) + (w2 * Vision) + (w3 * log(Cluster)) + (w4 * Context)
    And ensure proximity within 200m of a school triggers the vulnerability boost!
    """
    # Location 57m from Oakridge School
    oakridge_lat, oakridge_lng = 37.7753, -122.4190
    score = priority_engine.calculate_priority(
        nlp_urgency=92.0,
        vision_hazard=94.0,
        cluster_size=3,
        lat=oakridge_lat,
        lng=oakridge_lng,
        vocal_panic_score=92.0
    )
    assert score.total_score >= 80.0
    assert score.tier == "CRITICAL"
    assert score.nearby_critical_landmark is not None
    assert "Oakridge" in score.nearby_critical_landmark
    assert score.distance_to_landmark_meters < 200.0
    assert "P_score" in score.explanation
    assert "=" in score.formula_str

def test_audio_asr_and_regional_dialect_translation():
    """Verify regional dialect transcription and vocal panic detection."""
    res = multimodal_triage.analyze_audio(preset_key="sparking_wire_hindi")
    assert "Hindi" in res.detected_language
    assert res.vocal_emotion == "Panicked"
    assert res.acoustic_panic_score >= 85.0
    assert "transformer" in res.translated_english.lower()

def test_computer_vision_hazard_scoring():
    """Verify CV hazard detection on exposed wire."""
    res = multimodal_triage.analyze_vision(preset_key="sparking_wire")
    assert res.hazard_score >= 90.0
    assert res.hazard_level == "Extreme"
    assert res.bounding_box is not None
    assert len(res.detected_elements) > 0

def test_anti_fake_closure_guard_rejection():
    """Verify Anti-Fake closure guard blocks fake unrelated images."""
    complaint = db.get_complaint("CMP-7002")
    res = anti_fake_guard.evaluate_proof(
        complaint=complaint.dict(),
        after_preset="fake_unrelated",
        resolver_notes="Trying to close with cat photo"
    )
    assert res.verified is False
    assert res.fix_confidence < 30.0
    assert "REJECTION" in res.reason or "FRAUD" in res.reason
    assert res.cryptographic_token is None

def test_anti_fake_closure_guard_approval():
    """Verify Anti-Fake closure guard approves genuine repaired photo."""
    complaint = db.get_complaint("CMP-7002")
    res = anti_fake_guard.evaluate_proof(
        complaint=complaint.dict(),
        after_preset="genuine_repaired_pothole",
        resolver_notes="Completed hot-mix asphalt patch"
    )
    assert res.verified is True
    assert res.fix_confidence >= 95.0
    assert res.cryptographic_token is not None
    assert "CERT-VERIFIED" in res.cryptographic_token

def test_zero_touch_autonomous_resolution():
    """Verify Agentic Zero-Touch Auto-Resolver resolves digital invoice in ~4s."""
    complaint = db.get_complaint("CMP-7003")
    res = zero_touch_resolver.execute_resolution(complaint.dict())
    assert res.success is True
    assert len(res.actions_taken) >= 5
    assert res.refund_transaction_id is not None
    assert res.execution_time_seconds >= 3.0

def test_empathy_copilot_de_escalation():
    """Verify Empathy Copilot generates policy-backed de-escalating response."""
    complaint = db.get_complaint("CMP-7001")
    draft = empathy_copilot.generate_draft(complaint.dict(), tone="EMPATHETIC")
    assert draft.user_emotion == "Panicked"
    assert "perimeter" in draft.draft_message.lower()
    assert len(draft.policy_citations) > 0
    assert len(draft.recommended_actions) > 0

def test_simulate_mass_outage_crowd_swarm():
    """Verify Minute 2 demo mass outage simulation clusters 25 reports."""
    res = db.simulate_mass_outage()
    assert res["success"] is True
    assert res["complaints_created_count"] == 25
    assert res["master_incident"]["priority_tier"] == "CRITICAL"
    assert res["master_incident"]["complaint_count"] == 25

def test_swarm_clustering_radius_match():
    """Verify swarm clustering matches reports within radius and category."""
    masters = list(db.master_incidents.values())
    c = {
        "id": "TEST-C1",
        "category": "Public Utilities (Water & Hydro)",
        "description": "Water main gushing on Grand Ave",
        "latitude": 37.7831,
        "longitude": -122.4161
    }
    master = swarm_clustering.find_matching_master_incident(
        c["category"], c["description"], c["latitude"], c["longitude"], masters
    )
    assert master is not None
    title = master.title if hasattr(master, "title") else master["title"]
    assert "Water" in title

def test_database_state_and_landmarks():
    """Verify database fixtures and critical landmarks configuration."""
    assert len(db.complaints) >= 4
    assert len(settings.CRITICAL_LANDMARKS) >= 5
    assert any(lm["type"] == "HOSPITAL" for lm in settings.CRITICAL_LANDMARKS)
    assert any(lm["type"] == "SCHOOL" for lm in settings.CRITICAL_LANDMARKS)
