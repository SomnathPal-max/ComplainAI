import time
import uuid
import random
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from backend.models import Complaint, MasterIncident, ScoreBreakdown, AuditLogEntry
from backend.config import settings
from backend.ai.priority_engine import priority_engine

class Database:
    def __init__(self):
        self.complaints: Dict[str, Complaint] = {}
        self.master_incidents: Dict[str, MasterIncident] = {}
        self._seed_initial_data()

    def _seed_initial_data(self):
        now = datetime.utcnow()

        # Seed 1: The Sparking Wire near Oakridge School (Target for Minute 1 & Minute 3 Demo)
        c1_id = "CMP-7001"
        c1_lat, c1_lng = 37.7753, -122.4190  # 65 meters from Oakridge School!
        c1_score = priority_engine.calculate_priority(
            nlp_urgency=92.0,
            vision_hazard=94.0,
            cluster_size=3,
            lat=c1_lat,
            lng=c1_lng,
            vocal_panic_score=92.0
        )
        self.complaints[c1_id] = Complaint(
            id=c1_id,
            tracking_number="CMP-7001",
            title="Active Arc-Flashing Electrical Wire Hanging Outside Oakridge School",
            description="Exposed 4.8kV utility wire detached from crossarm and is violently sparking against chainlink fence. School recess bell about to ring.",
            original_transcript="Bhaiya yahan Oakridge school ke theek samne transformer se bohot tez sparks nikal rahe hain! Bachhe chutti hone pe nikalne wale hain, kisi ko current lag sakta hai, please turant kisi ko bhejo!",
            dialect="Urban North Indian / Hinglish Colloquial",
            translated_english="Brothers, right in front of Oakridge School, intense sparks are flying from the transformer! Kids are about to leave for recess, someone could get electrocuted, please send someone immediately!",
            category="Public Safety & Electrical",
            sub_tags=["High-Voltage Hazard", "Fire Risk", "Arc Flash Hazard", "Pedestrian Exposure"],
            sub_tag_confidences={"High-Voltage Hazard": 0.98, "Fire Risk": 0.91, "Pedestrian Exposure": 0.89},
            sentiment="Extreme Distress",
            vocal_emotion="Panicked",
            vocal_panic_score=92.0,
            visual_defect="Exposed High-Voltage Electrical Conductor & Arc Flash Ignition Hazard",
            visual_hazard_score=94.0,
            nlp_urgency_score=92.0,
            cluster_size=3,
            context_risk_score=c1_score.context_score,
            priority_score=c1_score.total_score,
            priority_tier=c1_score.tier,
            score_breakdown=c1_score,
            status="IN_PROGRESS",
            user_name="Aarav Sharma",
            user_phone="+1 (555) 948-2104",
            channel="PHONE_VOICE",
            location_name="Oakridge School Gate, Elm & 8th St",
            latitude=c1_lat,
            longitude=c1_lng,
            image_url="/static/images/sparking_wire.svg",
            created_at=(now - timedelta(minutes=35)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            sla_due_at=(now + timedelta(minutes=85)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            sla_seconds_remaining=5100,
            sla_escalated=False,
            audit_trail=[
                AuditLogEntry(
                    timestamp=(now - timedelta(minutes=35)).strftime("%H:%M:%S"),
                    event="SNAP_AND_SPEAK_TRIAGE",
                    actor="ComplainAI Multimodal VLM",
                    details="Audio distress parsed (92% panic). Visual hazard tagged 94/100. Proximity to Oakridge School triggered Vulnerability Boost (+19.4pts)."
                ),
                AuditLogEntry(
                    timestamp=(now - timedelta(minutes=25)).strftime("%H:%M:%S"),
                    event="DISPATCH_OVERRIDE",
                    actor="System Automation",
                    details="Tier 1 Rapid Response unit dispatched with high-voltage insulated bucket truck."
                )
            ]
        )

        # Seed 2: Pothole on 4th Street (Target for Anti-Fake Closure Demonstration)
        c2_id = "CMP-7002"
        c2_lat, c2_lng = 37.7790, -122.4120
        c2_score = priority_engine.calculate_priority(
            nlp_urgency=62.0,
            vision_hazard=64.0,
            cluster_size=1,
            lat=c2_lat,
            lng=c2_lng,
            vocal_panic_score=58.0
        )
        self.complaints[c2_id] = Complaint(
            id=c2_id,
            tracking_number="CMP-7002",
            title="Severe 8-Inch Asphalt Crater on 4th Street Bicycle Lane",
            description="Deep cavity with exposed sub-base rock. Cyclists and scooters are swerving into oncoming vehicular traffic to avoid it.",
            category="Municipal Infrastructure (Roads)",
            sub_tags=["Severe Pothole", "Traffic Collision Risk", "Pavement Structural Void"],
            sub_tag_confidences={"Severe Pothole": 0.94, "Traffic Collision Risk": 0.79},
            sentiment="Frustrated",
            vocal_emotion="Frustrated",
            vocal_panic_score=58.0,
            visual_defect="Severe Structural Asphalt Cavity & Sub-base Void",
            visual_hazard_score=64.0,
            nlp_urgency_score=62.0,
            cluster_size=1,
            context_risk_score=c2_score.context_score,
            priority_score=c2_score.total_score,
            priority_tier=c2_score.tier,
            score_breakdown=c2_score,
            status="IN_PROGRESS",
            user_name="Marcus Vance",
            user_phone="+1 (555) 302-8841",
            channel="WEB",
            location_name="4th St & Bryant Ave (Northbound)",
            latitude=c2_lat,
            longitude=c2_lng,
            image_url="/static/images/pothole.svg",
            created_at=(now - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            sla_due_at=(now + timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            sla_seconds_remaining=14400,
            sla_escalated=False,
            audit_trail=[
                AuditLogEntry(
                    timestamp=(now - timedelta(hours=2)).strftime("%H:%M:%S"),
                    event="INTAKE_CLASSIFIED",
                    actor="ComplainAI Engine",
                    details="Surface cavity classified. Work order #WO-409 created for Roadway Maintenance."
                )
            ]
        )

        # Seed 3: Duplicate Billing Charge (Target for Agentic Zero-Touch Auto-Resolver)
        c3_id = "CMP-7003"
        c3_score = priority_engine.calculate_priority(
            nlp_urgency=38.0,
            vision_hazard=0.0,
            cluster_size=1,
            lat=37.7749,
            lng=-122.4194,
            vocal_panic_score=24.0
        )
        self.complaints[c3_id] = Complaint(
            id=c3_id,
            tracking_number="CMP-7003",
            title="Duplicate Monthly Charge on Invoice INV-402 ($89.00)",
            description="I was charged twice on October 28th for my Fiber 1Gbps plan ($89.00 x 2). Account #ACC-88321.",
            category="Billing & Financial Services",
            sub_tags=["Duplicate Transaction", "Invoice Discrepancy", "Automated Refund Candidate"],
            sub_tag_confidences={"Duplicate Transaction": 0.99, "Automated Refund Candidate": 0.95},
            sentiment="Neutral",
            vocal_emotion="Calm",
            vocal_panic_score=24.0,
            visual_defect="Digital Billing Statement with Duplicate Line Item ($89.00)",
            visual_hazard_score=0.0,
            nlp_urgency_score=38.0,
            cluster_size=1,
            context_risk_score=c3_score.context_score,
            priority_score=c3_score.total_score,
            priority_tier=c3_score.tier,
            score_breakdown=c3_score,
            status="TRIAGED",
            user_name="Elena Rostova",
            user_phone="+1 (555) 714-9923",
            channel="WEB",
            location_name="Account Portal / Digital Ingestion",
            latitude=37.7749,
            longitude=-122.4194,
            image_url="/static/images/billing.svg",
            created_at=(now - timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            sla_due_at=(now + timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            sla_seconds_remaining=85500,
            sla_escalated=False,
            auto_resolved=False,
            audit_trail=[
                AuditLogEntry(
                    timestamp=(now - timedelta(minutes=15)).strftime("%H:%M:%S"),
                    event="ZERO_TOUCH_ELIGIBLE",
                    actor="Agentic Classifier",
                    details="Identified as Tier-1 digital invoice discrepancy. Ready for autonomous tool execution."
                )
            ]
        )

        # Seed 4: Water Main Rupture Master Incident (Existing cluster)
        m1_id = "MASTER-INC-202"
        m1_lat, m1_lng = 37.7830, -122.4160  # Near St. Jude Hospital!
        self.master_incidents[m1_id] = MasterIncident(
            id=m1_id,
            title="12-Inch Subterranean Water Main Rupture & Roadway Flooding",
            category="Public Utilities (Water & Hydro)",
            sub_tag="Water Main Rupture",
            complaint_count=14,
            complaint_ids=["CMP-6101", "CMP-6102", "CMP-6103"],
            center_latitude=m1_lat,
            center_longitude=m1_lng,
            location_name="Grand Ave Corridor (St. Jude Hospital Frontage)",
            hazard_level="Severe",
            priority_score=89.6,
            priority_tier="CRITICAL",
            status="ACTIVE",
            created_at=(now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            updated_at=now.strftime("%Y-%m-%dT%H:%M:%SZ")
        )

    def get_all_complaints(self) -> List[Complaint]:
        return sorted(list(self.complaints.values()), key=lambda c: c.priority_score, reverse=True)

    def get_complaint(self, complaint_id: str) -> Optional[Complaint]:
        return self.complaints.get(complaint_id)

    def search_complaints(self, query: str) -> List[Complaint]:
        q = query.strip().lower()
        if not q:
            return self.get_all_complaints()
        results = []
        for c in self.complaints.values():
            if (q in c.id.lower() or 
                q in c.tracking_number.lower() or 
                (c.user_phone and q in c.user_phone.lower()) or 
                q in c.title.lower() or 
                q in c.location_name.lower() or
                q in c.category.lower()):
                results.append(c)
        return sorted(results, key=lambda x: x.priority_score, reverse=True)

    def save_complaint(self, complaint: Complaint):
        self.complaints[complaint.id] = complaint

    def get_all_masters(self) -> List[MasterIncident]:
        return sorted(list(self.master_incidents.values()), key=lambda m: m.priority_score, reverse=True)

    def get_master(self, master_id: str) -> Optional[MasterIncident]:
        return self.master_incidents.get(master_id)

    def simulate_mass_outage(self) -> Dict[str, Any]:
        """
        Minute 2 Demo Pitch Feature:
        Fires 25 citizen complaints across Sector 4 within 250m of Sector 4 Transformer Substation.
        Clusters all 25 into one pulsing red Master Incident pin, dynamically boosting priority to Critical!
        """
        now = datetime.utcnow()
        master_id = f"MASTER-OUTAGE-{int(time.time())}"
        center_lat = 37.7650
        center_lng = -122.4300
        location_name = "Sector 4 Electrical Grid Substation Zone"

        citizen_names = [
            "David Chen", "Sarah Miller", "Rajesh Patel", "Maria Gonzalez", "James Wilson",
            "Chloe Dupont", "Liam O'Connor", "Fatima Al-Mansoor", "Sergei Volkov", "Priya Nair",
            "Carlos Mendez", "Hannah Schmidt", "Devon Taylor", "Aisha Abubakar", "Kenji Sato",
            "Emily Watson", "Ahmed Hassan", "Lucia Rossi", "Tariq Mahmood", "Grace Hopper",
            "Zane Grey", "Olivia Benson", "Mateo Rivera", "Sophie Dubois", "Vikram Malhotra"
        ]

        outage_descriptions = [
            "Sudden loud electrical explosion heard from substation. All power cut off in Block 12.",
            "Lights violently flickered then entire street plunged into total blackout.",
            "My medical oxygen concentrator just shut down due to complete power failure in Sector 4!",
            "Voltage surge blew out our router and television before power died completely.",
            "Traffic lights at 14th and Market are dead, major gridlock forming.",
            "Smell of burning electrical oil near the transformer fence. Whole block is dark.",
            "Emergency power cut! Elevator stuck between 4th and 5th floors in residential building.",
            "Complete grid outage across Sector 4. No street lights or home power."
        ]

        generated_complaint_ids = []

        for i, name in enumerate(citizen_names):
            c_id = f"CMP-SWARM-{1000 + i}"
            offset_lat = center_lat + random.uniform(-0.0018, 0.0018)
            offset_lng = center_lng + random.uniform(-0.0018, 0.0018)
            desc = random.choice(outage_descriptions)

            score_res = priority_engine.calculate_priority(
                nlp_urgency=90.0,
                vision_hazard=85.0,
                cluster_size=i + 1,
                lat=offset_lat,
                lng=offset_lng,
                vocal_panic_score=85.0
            )

            complaint = Complaint(
                id=c_id,
                tracking_number=c_id,
                title=f"Catastrophic Sector 4 Grid Blackout (Report #{i+1})",
                description=desc,
                category="Public Safety & Electrical",
                sub_tags=["Grid Blackout", "Transformer Blowout", "Vulnerable Life Safety", "Mass Outage"],
                sub_tag_confidences={"Grid Blackout": 0.99, "Transformer Blowout": 0.95},
                sentiment="Extreme Distress",
                vocal_emotion="Panicked",
                vocal_panic_score=85.0,
                visual_defect="High-Voltage Transformer Substation Explosion & Arc Discharge",
                visual_hazard_score=88.0,
                nlp_urgency_score=90.0,
                cluster_size=25,
                context_risk_score=score_res.context_score,
                priority_score=score_res.total_score,
                priority_tier=score_res.tier,
                score_breakdown=score_res,
                status="TRIAGED",
                master_incident_id=master_id,
                is_master=False,
                user_name=name,
                user_phone=f"+1 (555) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
                channel=random.choice(["WEB", "WHATSAPP", "PHONE_VOICE"]),
                location_name=location_name,
                latitude=offset_lat,
                longitude=offset_lng,
                image_url="/static/images/sparking_wire.svg",
                created_at=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                sla_due_at=(now + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                sla_seconds_remaining=7200,
                sla_escalated=False,
                audit_trail=[
                    AuditLogEntry(
                        timestamp=now.strftime("%H:%M:%S"),
                        event="SWARM_DEDUPLICATION",
                        actor="ComplainAI Clustering Engine",
                        details=f"Citizen complaint auto-merged into Master Incident {master_id}. Logarithmic crowd density multiplier applied."
                    )
                ]
            )
            self.complaints[c_id] = complaint
            generated_complaint_ids.append(c_id)

        # Recalculate Master Incident with 25 complaints
        master_score = priority_engine.calculate_priority(
            nlp_urgency=95.0,
            vision_hazard=92.0,
            cluster_size=25,
            lat=center_lat,
            lng=center_lng,
            vocal_panic_score=90.0
        )

        master_incident = MasterIncident(
            id=master_id,
            title="CRITICAL MASS OUTAGE: Sector 4 Substation Explosion & 25-User Swarm",
            category="Public Safety & Electrical",
            sub_tag="Sector 4 Grid Failure",
            complaint_count=25,
            complaint_ids=generated_complaint_ids,
            center_latitude=center_lat,
            center_longitude=center_lng,
            location_name=location_name,
            hazard_level="Extreme",
            priority_score=master_score.total_score,  # ~98/100
            priority_tier="CRITICAL",
            status="ACTIVE",
            created_at=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            updated_at=now.strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        self.master_incidents[master_id] = master_incident

        return {
            "success": True,
            "master_incident": master_incident.dict(),
            "complaints_created_count": len(generated_complaint_ids),
            "swarmed_ids": generated_complaint_ids[:5],
            "message": f"Successfully simulated 25 concurrent complaints in Sector 4! Deduplicated into 1 Master Incident with priority boosted to {master_score.total_score}/100 [CRITICAL]."
        }

db = Database()
