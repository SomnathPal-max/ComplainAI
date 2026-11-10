import math
from typing import Tuple, Optional, Dict
from backend.config import settings
from backend.models import ScoreBreakdown

def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

class PriorityEngine:
    def __init__(self):
        self.w1 = settings.WEIGHT_NLP
        self.w2 = settings.WEIGHT_VISION
        self.w3 = settings.WEIGHT_CLUSTER
        self.w4 = settings.WEIGHT_CONTEXT

    def calculate_context_risk(self, lat: float, lng: float) -> Tuple[float, Optional[str], Optional[float]]:
        """
        Calculates GIS Environmental Context Risk with Vulnerability Boost.
        Checks proximity to hospitals, schools, vulnerable elderly populations, and critical grids.
        """
        closest_landmark = None
        min_dist = float("inf")
        context_score = 20.0  # baseline urban context risk

        for lm in settings.CRITICAL_LANDMARKS:
            dist = haversine_distance_meters(lat, lng, lm["latitude"], lm["longitude"])
            if dist < min_dist:
                min_dist = dist
                closest_landmark = lm

        if closest_landmark:
            # If within 200m of critical infrastructure, trigger major vulnerability spike!
            if min_dist <= settings.CRITICAL_INFRA_RADIUS_METERS:
                proximity_factor = max(0.0, 1.0 - (min_dist / settings.CRITICAL_INFRA_RADIUS_METERS))
                # Base critical spike 75-98 based on proximity and landmark multiplier
                context_score = min(100.0, 75.0 + (proximity_factor * 20.0) * closest_landmark.get("risk_multiplier", 1.2))
                return context_score, closest_landmark["name"], round(min_dist, 1)
            elif min_dist <= 500.0:
                # Moderate proximity buffer
                context_score = 45.0 + (1.0 - (min_dist / 500.0)) * 25.0
                return context_score, closest_landmark["name"], round(min_dist, 1)

        return context_score, closest_landmark["name"] if closest_landmark else None, round(min_dist, 1) if closest_landmark else None

    def calculate_priority(
        self,
        nlp_urgency: float,
        vision_hazard: float,
        cluster_size: int,
        lat: float,
        lng: float,
        vocal_panic_score: float = 0.0
    ) -> ScoreBreakdown:
        """
        Calculates dynamic multi-factor priority index:
        P_score = (w1 * NLP) + (w2 * Vision) + (w3 * log(Cluster)) + (w4 * Context)
        """
        # 1. NLP factor incorporates both text classification & acoustic distress
        effective_nlp = max(nlp_urgency, vocal_panic_score)

        # 2. Vision factor
        effective_vision = max(0.0, min(100.0, vision_hazard))

        # 3. Logarithmic Swarm Clustering multiplier: log(N + 1) normalized to 0-100
        # If cluster_size is 1, score is 0. If cluster_size is 25, score reaches ~96
        log_scale = math.log(max(1, cluster_size) + 0.1)
        cluster_score = min(100.0, (log_scale / math.log(30.0)) * 100.0)

        # 4. Context risk with GIS Vulnerability Boost
        context_score, landmark_name, landmark_dist = self.calculate_context_risk(lat, lng)

        # Weighted calculation
        weighted_nlp = self.w1 * effective_nlp
        weighted_vision = self.w2 * effective_vision
        weighted_cluster = self.w3 * cluster_score
        weighted_context = self.w4 * context_score

        total_score = min(100.0, max(0.0, weighted_nlp + weighted_vision + weighted_cluster + weighted_context))
        total_score = round(total_score, 1)

        # Determine Tier
        if total_score >= 80.0:
            tier = "CRITICAL"
        elif total_score >= 60.0:
            tier = "HIGH"
        elif total_score >= 40.0:
            tier = "MEDIUM"
        else:
            tier = "LOW"

        # Explainable breakdown string
        breakdown_parts = [
            f"+{weighted_nlp:.1f} NLP/Vocal Urgency ({effective_nlp:.0f}%)",
            f"+{weighted_vision:.1f} Visual Hazard ({effective_vision:.0f}%)",
            f"+{weighted_cluster:.1f} Swarm Cluster ({cluster_size} reports)",
        ]
        if landmark_name and landmark_dist is not None and landmark_dist <= 350:
            breakdown_parts.append(f"+{weighted_context:.1f} Vulnerability Boost ({landmark_name} @ {landmark_dist:.0f}m)")
        else:
            breakdown_parts.append(f"+{weighted_context:.1f} Base Context ({context_score:.0f}%)")

        explanation = f"P_score = {total_score}/100 [{tier}] breakdown: " + " | ".join(breakdown_parts)
        formula_str = f"({self.w1:.2f} × {effective_nlp:.0f}) + ({self.w2:.2f} × {effective_vision:.0f}) + ({self.w3:.2f} × {cluster_score:.0f}) + ({self.w4:.2f} × {context_score:.0f}) = {total_score:.1f}"

        return ScoreBreakdown(
            nlp_score=round(effective_nlp, 1),
            vision_score=round(effective_vision, 1),
            cluster_score=round(cluster_score, 1),
            context_score=round(context_score, 1),
            weighted_nlp=round(weighted_nlp, 1),
            weighted_vision=round(weighted_vision, 1),
            weighted_cluster=round(weighted_cluster, 1),
            weighted_context=round(weighted_context, 1),
            total_score=total_score,
            tier=tier,
            formula_str=formula_str,
            explanation=explanation,
            nearby_critical_landmark=landmark_name,
            distance_to_landmark_meters=landmark_dist
        )

priority_engine = PriorityEngine()
