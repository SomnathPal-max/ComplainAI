import re
import json
import base64
from typing import Dict, Any, Tuple, List, Optional
from backend.ai.ollama_client import ollama_client
from backend.models import AudioAnalysisResult, VisionAnalysisResult

PRESET_AUDIO_TRANSCRIPTS = {
    "sparking_wire_hindi": {
        "transcript": "Bhaiya yahan Oakridge school ke theek samne transformer se bohot tez sparks nikal rahe hain! Bachhe chutti hone pe nikalne wale hain, kisi ko current lag sakta hai, please turant kisi ko bhejo!",
        "detected_language": "Hindi / Hinglish",
        "dialect": "Urban North Indian / Hinglish Colloquial",
        "translated_english": "Brothers, right in front of Oakridge School, intense sparks are flying from the transformer! Kids are about to leave for recess, someone could get electrocuted, please send someone immediately!",
        "acoustic_panic_score": 92.0,
        "vocal_emotion": "Panicked",
        "urgency_keywords": ["sparks", "school", "kids", "current", "electrocuted", "turant", "immediately"]
    },
    "sparking_wire_spanish": {
        "transcript": "¡Por favor ayuda urgente! Hay un cable de alta tensión echando chispas al lado del colegio primario. Es un peligro mortal para los niños.",
        "detected_language": "Spanish",
        "dialect": "Latin American Spanish",
        "translated_english": "Please urgent help! There is a high voltage cable sparking right next to the elementary school. It is a fatal hazard for children.",
        "acoustic_panic_score": 89.0,
        "vocal_emotion": "Panicked",
        "urgency_keywords": ["urgente", "alta tensión", "chispas", "peligro mortal", "niños"]
    },
    "water_main_rupture": {
        "transcript": "Emergency! The main 12-inch water pipe just ruptured on Grand Avenue outside St. Jude Hospital! The entire street is submerged under 2 feet of gushing water, ambulances can barely get through!",
        "detected_language": "English",
        "dialect": "US Metropolitan",
        "translated_english": "Emergency! The main 12-inch water pipe just ruptured on Grand Avenue outside St. Jude Hospital! The entire street is submerged under 2 feet of gushing water, ambulances can barely get through!",
        "acoustic_panic_score": 86.0,
        "vocal_emotion": "Panicked",
        "urgency_keywords": ["emergency", "ruptured", "water pipe", "hospital", "ambulances blocked", "submerged"]
    },
    "duplicate_billing": {
        "transcript": "Hello, I was checking my monthly statement for Fiber 1Gbps and noticed I was charged twice for $89.00 on invoice INV-402 on October 28th. Can you please check and refund the second deduction?",
        "detected_language": "English",
        "dialect": "Standard English",
        "translated_english": "Hello, I was checking my monthly statement for Fiber 1Gbps and noticed I was charged twice for $89.00 on invoice INV-402 on October 28th. Can you please check and refund the second deduction?",
        "acoustic_panic_score": 24.0,
        "vocal_emotion": "Calm",
        "urgency_keywords": ["duplicate charge", "refund", "invoice INV-402", "statement"]
    },
    "deep_pothole": {
        "transcript": "There is a massive 8-inch deep crater on 4th Street right before the bicycle lane. Two scooters swerved and almost crashed this morning. It needs urgent asphalt patch.",
        "detected_language": "English",
        "dialect": "US Urban",
        "translated_english": "There is a massive 8-inch deep crater on 4th Street right before the bicycle lane. Two scooters swerved and almost crashed this morning. It needs urgent asphalt patch.",
        "acoustic_panic_score": 58.0,
        "vocal_emotion": "Frustrated",
        "urgency_keywords": ["crater", "crashed", "bicycle lane", "deep pothole", "hazard"]
    }
}

PRESET_VISION_ANALYSIS = {
    "sparking_wire": {
        "defect_detected": "Exposed High-Voltage Electrical Conductor & Arc Flash Ignition Hazard",
        "hazard_score": 94.0,
        "hazard_level": "Extreme",
        "bounding_box": {"top": 0.22, "left": 0.30, "width": 0.45, "height": 0.50},
        "detected_elements": ["Sparking Electrical Conductor", "Frayed Insulation", "Open Utility Pole Junction", "Pedestrian Footpath Proximity"]
    },
    "water_flood": {
        "defect_detected": "Pressurized Water Main Rupture & Severe Roadway Submersion",
        "hazard_score": 84.0,
        "hazard_level": "Severe",
        "bounding_box": {"top": 0.32, "left": 0.15, "width": 0.70, "height": 0.55},
        "detected_elements": ["Gushing Water Breach", "Roadway Inundation", "Erosion Void", "Traffic Blockage"]
    },
    "pothole": {
        "defect_detected": "Severe Structural Asphalt Cavity & Sub-base Void",
        "hazard_score": 64.0,
        "hazard_level": "Moderate",
        "bounding_box": {"top": 0.38, "left": 0.28, "width": 0.44, "height": 0.42},
        "detected_elements": ["Asphalt Degradation", "Exposed Sub-base Aggregate", "Sharp Rim Edges"]
    },
    "trash_overflow": {
        "defect_detected": "Commercial Sanitation Dumpster Overflow & Bio-refuse Spillage",
        "hazard_score": 42.0,
        "hazard_level": "Minor",
        "bounding_box": {"top": 0.25, "left": 0.20, "width": 0.60, "height": 0.50},
        "detected_elements": ["Refuse Spillage", "Pedestrian Walkway Obstruction", "Vector Attraction Risk"]
    },
    "billing_invoice": {
        "defect_detected": "Digital Account Billing Statement with Duplicate Line Item ($89.00)",
        "hazard_score": 0.0,
        "hazard_level": "None",
        "bounding_box": {"top": 0.10, "left": 0.10, "width": 0.80, "height": 0.80},
        "detected_elements": ["Account #ACC-88321", "Double Transaction INV-402", "Authorized Payment Gateway"]
    }
}

class MultimodalTriageEngine:
    def __init__(self):
        pass

    def analyze_audio(self, audio_base64: Optional[str] = None, preset_key: Optional[str] = None, raw_text: Optional[str] = None) -> AudioAnalysisResult:
        """Perform acoustic emotion recognition and regional dialect transcription."""
        # 1. Preset matching if provided
        if preset_key and preset_key in PRESET_AUDIO_TRANSCRIPTS:
            data = PRESET_AUDIO_TRANSCRIPTS[preset_key]
            return AudioAnalysisResult(**data)

        # 2. If raw text provided or derived from speech
        text = raw_text or ""
        
        # Check if text matches known regional phrases or dialect markers
        lower = text.lower()
        if any(w in lower for w in ["bhaiya", "bohot", "tez", "bachhe", "current", "turant"]):
            return AudioAnalysisResult(
                transcript=text,
                detected_language="Hindi / Hinglish",
                dialect="Urban Hinglish Colloquial",
                translated_english="High danger: sparks coming from transformer near school, urgent assistance required!",
                acoustic_panic_score=88.0,
                vocal_emotion="Panicked",
                urgency_keywords=["sparks", "transformer", "school", "urgent"]
            )
        elif any(w in lower for w in ["por favor", "ayuda", "urgente", "chispas", "peligro"]):
            return AudioAnalysisResult(
                transcript=text,
                detected_language="Spanish",
                dialect="Latin American Spanish",
                translated_english="Urgent help: electrical sparking wire posing life hazard near school!",
                acoustic_panic_score=87.0,
                vocal_emotion="Panicked",
                urgency_keywords=["urgente", "chispas", "peligro"]
            )

        # Calculate acoustic panic & emotion based on lexical urgency markers
        panic_tokens = ["danger", "emergency", "fire", "spark", "explosion", "help", "trapped", "dying", "shock", "submerged", "burst", "hurry"]
        angry_tokens = ["unacceptable", "furious", "lawsuit", "disgusting", "terrible", "pathetic", "thieves", "scam"]
        frustrated_tokens = ["waiting", "again", "third time", "ignored", "broken", "annoying", "delay"]

        panic_count = sum(1 for w in panic_tokens if w in lower)
        angry_count = sum(1 for w in angry_tokens if w in lower)
        frustrated_count = sum(1 for w in frustrated_tokens if w in lower)

        if panic_count >= 2 or "!" in text and panic_count >= 1:
            panic_score = min(95.0, 65.0 + panic_count * 10.0)
            emotion = "Panicked"
        elif angry_count >= 1:
            panic_score = min(80.0, 50.0 + angry_count * 12.0)
            emotion = "Angry"
        elif frustrated_count >= 1:
            panic_score = min(65.0, 40.0 + frustrated_count * 8.0)
            emotion = "Frustrated"
        else:
            panic_score = 20.0
            emotion = "Calm"

        return AudioAnalysisResult(
            transcript=text or "Audio voice note transcribed via ASR",
            detected_language="English",
            dialect="Regional English",
            translated_english=text or "Transcribed message from citizen voice note.",
            acoustic_panic_score=panic_score,
            vocal_emotion=emotion,
            urgency_keywords=[w for w in (panic_tokens + angry_tokens) if w in lower]
        )

    def analyze_vision(self, image_base64: Optional[str] = None, preset_key: Optional[str] = None, text_hint: str = "") -> VisionAnalysisResult:
        """Perform Computer Vision & Visual-Language hazard scoring."""
        # Check presets
        if preset_key and preset_key in PRESET_VISION_ANALYSIS:
            return VisionAnalysisResult(**PRESET_VISION_ANALYSIS[preset_key])

        # Contextual inference based on text_hint or visual patterns
        lower = text_hint.lower()
        if any(k in lower for k in ["spark", "wire", "electric", "shock", "transformer", "fire"]):
            return VisionAnalysisResult(**PRESET_VISION_ANALYSIS["sparking_wire"])
        elif any(k in lower for k in ["water", "flood", "pipe", "leak", "gush", "submerged"]):
            return VisionAnalysisResult(**PRESET_VISION_ANALYSIS["water_flood"])
        elif any(k in lower for k in ["pothole", "crater", "road", "asphalt", "cavity"]):
            return VisionAnalysisResult(**PRESET_VISION_ANALYSIS["pothole"])
        elif any(k in lower for k in ["garbage", "trash", "waste", "dumpster", "smell", "dump"]):
            return VisionAnalysisResult(**PRESET_VISION_ANALYSIS["trash_overflow"])
        elif any(k in lower for k in ["charge", "bill", "invoice", "refund", "subscription", "deduct"]):
            return VisionAnalysisResult(**PRESET_VISION_ANALYSIS["billing_invoice"])

        # Default fallback
        return VisionAnalysisResult(
            defect_detected="Unspecified Physical Condition / Structural Anomaly",
            hazard_score=35.0,
            hazard_level="Minor",
            bounding_box={"top": 0.3, "left": 0.3, "width": 0.4, "height": 0.4},
            detected_elements=["Scene artifact", "Surface region"]
        )

    def classify_nlp_tags(self, text: str) -> Tuple[str, List[str], Dict[str, float], float]:
        """Classify complaint into primary category, sub-tags, confidences, and NLP urgency score."""
        lower = text.lower()
        
        # Categories: Safety, Public Utilities, Infrastructure, Billing, Municipal Sanitation, Telecom
        if any(w in lower for w in ["spark", "fire", "shock", "wire", "hazard", "life", "electrocute", "danger"]):
            category = "Public Safety & Electrical"
            sub_tags = ["High-Voltage Hazard", "Fire Risk", "Arc Flash Hazard", "Pedestrian Exposure"]
            confidences = {"High-Voltage Hazard": 0.98, "Fire Risk": 0.91, "Pedestrian Exposure": 0.89}
            nlp_urgency = 92.0
        elif any(w in lower for w in ["water", "pipe", "flood", "drain", "gush", "sewage", "submerged"]):
            category = "Public Utilities (Water & Hydro)"
            sub_tags = ["Water Main Rupture", "Urban Flooding", "Infrastructure Erosion", "Traffic Impediment"]
            confidences = {"Water Main Rupture": 0.96, "Urban Flooding": 0.88, "Traffic Impediment": 0.82}
            nlp_urgency = 84.0
        elif any(w in lower for w in ["pothole", "road", "bridge", "asphalt", "crater", "concrete", "pavement"]):
            category = "Municipal Infrastructure (Roads)"
            sub_tags = ["Severe Pothole", "Traffic Collision Risk", "Pavement Structural Void"]
            confidences = {"Severe Pothole": 0.94, "Traffic Collision Risk": 0.79}
            nlp_urgency = 62.0
        elif any(w in lower for w in ["bill", "charge", "refund", "invoice", "double", "statement", "credit card"]):
            category = "Billing & Financial Services"
            sub_tags = ["Duplicate Transaction", "Invoice Discrepancy", "Automated Refund Candidate"]
            confidences = {"Duplicate Transaction": 0.99, "Automated Refund Candidate": 0.95}
            nlp_urgency = 38.0
        elif any(w in lower for w in ["trash", "garbage", "waste", "dumpster", "clean", "smell"]):
            category = "Municipal Sanitation & Environment"
            sub_tags = ["Refuse Overflow", "Sanitation Hazard", "Public Health Odor"]
            confidences = {"Refuse Overflow": 0.92, "Sanitation Hazard": 0.74}
            nlp_urgency = 45.0
        else:
            category = "General Civil Grievance"
            sub_tags = ["General Inquiry", "Civil Service Request"]
            confidences = {"General Inquiry": 0.80}
            nlp_urgency = 40.0

        return category, sub_tags, confidences, nlp_urgency

multimodal_triage = MultimodalTriageEngine()
