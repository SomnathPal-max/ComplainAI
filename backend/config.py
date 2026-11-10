import os
from typing import List, Dict

class Settings:
    # Ollama settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2-vision")
    OLLAMA_EMBED_MODEL: str = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    OLLAMA_TIMEOUT: float = 8.0  # seconds

    # Priority formula weights: P_score = (w1 * NLP) + (w2 * Vision) + (w3 * log(Cluster)) + (w4 * Context)
    WEIGHT_NLP: float = 0.35
    WEIGHT_VISION: float = 0.30
    WEIGHT_CLUSTER: float = 0.15
    WEIGHT_CONTEXT: float = 0.20

    # Geospatial clustering threshold in meters
    CLUSTER_RADIUS_METERS: float = 350.0

    # Proximity threshold for critical infrastructure vulnerability boost
    CRITICAL_INFRA_RADIUS_METERS: float = 200.0

    # SLA Durations (in seconds for live demo, realistic times mapped to countdowns)
    SLA_DURATIONS_MINUTES = {
        "CRITICAL": 120,   # 2 hours
        "HIGH": 360,       # 6 hours
        "MEDIUM": 1440,    # 24 hours
        "LOW": 2880        # 48 hours
    }

    # Known Critical Infrastructure Landmarks for Vulnerability Boost
    CRITICAL_LANDMARKS: List[Dict] = [
        {
            "id": "hosp-01",
            "name": "St. Jude Metropolitan Hospital",
            "type": "HOSPITAL",
            "latitude": 37.7833,
            "longitude": -122.4167,
            "risk_multiplier": 1.45,
            "description": "Level 1 Trauma Center & Pediatric ICU"
        },
        {
            "id": "sch-01",
            "name": "Oakridge Elementary & Middle School",
            "type": "SCHOOL",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "risk_multiplier": 1.40,
            "description": "Public school campus with 1,200 students"
        },
        {
            "id": "sub-04",
            "name": "Sector 4 High-Voltage Transformer Grid",
            "type": "POWER_GRID",
            "latitude": 37.7650,
            "longitude": -122.4300,
            "risk_multiplier": 1.50,
            "description": "Supplies power to 45,000 homes and metro hospital"
        },
        {
            "id": "water-02",
            "name": "Metro Central Water Treatment Station",
            "type": "WATER_UTILITY",
            "latitude": 37.7550,
            "longitude": -122.4200,
            "risk_multiplier": 1.35,
            "description": "Potable water pumping reservoir"
        },
        {
            "id": "senior-01",
            "name": "Golden Horizon Senior Assisted Living",
            "type": "VULNERABLE_POPULATION",
            "latitude": 37.7710,
            "longitude": -122.4110,
            "risk_multiplier": 1.40,
            "description": "350 elderly residents dependent on oxygen equipment"
        }
    ]

settings = Settings()
