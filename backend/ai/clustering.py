import time
import math
import uuid
from typing import List, Dict, Optional, Tuple, Any
from backend.ai.priority_engine import haversine_distance_meters, priority_engine
from backend.config import settings

def calculate_text_similarity(text1: str, text2: str) -> float:
    """Compute semantic Jaccard & token similarity for fast deduplication."""
    t1_tokens = set(text1.lower().replace(",", " ").replace(".", " ").split())
    t2_tokens = set(text2.lower().replace(",", " ").replace(".", " ").split())
    # remove common stop words
    stops = {"the", "a", "an", "is", "in", "at", "of", "on", "and", "to", "for", "it", "with", "from"}
    t1_tokens = {w for w in t1_tokens if w not in stops and len(w) > 2}
    t2_tokens = {w for w in t2_tokens if w not in stops and len(w) > 2}

    if not t1_tokens or not t2_tokens:
        return 0.0
    intersection = t1_tokens.intersection(t2_tokens)
    union = t1_tokens.union(t2_tokens)
    return len(intersection) / len(union)

class SwarmClusteringEngine:
    def __init__(self, radius_meters: float = settings.CLUSTER_RADIUS_METERS):
        self.radius_meters = radius_meters

    def find_matching_master_incident(
        self,
        category: str,
        description: str,
        lat: float,
        lng: float,
        existing_masters: List[Any]
    ) -> Optional[Any]:
        """
        Check if an incoming report belongs to an existing Master Incident
        using dual-condition matching: Category/Semantic similarity AND Geospatial proximity.
        """
        for master in existing_masters:
            status = getattr(master, "status", None) if not isinstance(master, dict) else master.get("status")
            if status != "ACTIVE":
                continue

            center_lat = getattr(master, "center_latitude", None) if not isinstance(master, dict) else master.get("center_latitude")
            center_lng = getattr(master, "center_longitude", None) if not isinstance(master, dict) else master.get("center_longitude")
            master_cat = getattr(master, "category", None) if not isinstance(master, dict) else master.get("category")
            master_title = getattr(master, "title", "") if not isinstance(master, dict) else master.get("title", "")
            master_subtag = getattr(master, "sub_tag", "") if not isinstance(master, dict) else master.get("sub_tag", "")

            # 1. Geographic radius test
            dist = haversine_distance_meters(lat, lng, center_lat, center_lng)
            if dist > self.radius_meters:
                continue

            # 2. Category or semantic match test
            if master_cat == category:
                return master

            # 3. Text similarity test
            sim = calculate_text_similarity(description, master_title + " " + master_subtag)
            if sim > 0.25:
                return master

        return None

    def create_or_join_cluster(
        self,
        complaint: Dict,
        existing_masters: List[Any]
    ) -> Tuple[Optional[str], bool, int]:
        """
        Returns (master_incident_id, is_new_master, cluster_size)
        """
        matching = self.find_matching_master_incident(
            complaint["category"],
            complaint["description"],
            complaint["latitude"],
            complaint["longitude"],
            existing_masters
        )

        if matching:
            # Join existing master
            m_id = getattr(matching, "id", None) if not isinstance(matching, dict) else matching.get("id")
            count = getattr(matching, "complaint_count", 1) if not isinstance(matching, dict) else matching.get("complaint_count", 1)
            count += 1
            if isinstance(matching, dict):
                matching["complaint_count"] = count
                if complaint["id"] not in matching["complaint_ids"]:
                    matching["complaint_ids"].append(complaint["id"])
                matching["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
                c_lat = matching["center_latitude"]
                c_lng = matching["center_longitude"]
            else:
                matching.complaint_count = count
                if complaint["id"] not in matching.complaint_ids:
                    matching.complaint_ids.append(complaint["id"])
                matching.updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ")
                c_lat = matching.center_latitude
                c_lng = matching.center_longitude

            # Dynamic priority boost due to swarm
            recalc = priority_engine.calculate_priority(
                nlp_urgency=complaint.get("nlp_urgency_score", 70.0),
                vision_hazard=complaint.get("visual_hazard_score", 60.0),
                cluster_size=count,
                lat=c_lat,
                lng=c_lng,
                vocal_panic_score=complaint.get("vocal_panic_score", 0.0)
            )
            if isinstance(matching, dict):
                matching["priority_score"] = recalc.total_score
                matching["priority_tier"] = recalc.tier
            else:
                matching.priority_score = recalc.total_score
                matching.priority_tier = recalc.tier

            return m_id, False, count

        return None, False, 1

swarm_clustering = SwarmClusteringEngine()
