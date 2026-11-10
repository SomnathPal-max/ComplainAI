import time
import uuid
import random
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from backend.models import Complaint, MasterIncident, ScoreBreakdown, AuditLogEntry, UserProfile, FacultyScorecard
from backend.config import settings
from backend.ai.priority_engine import priority_engine

# Pre-configured Demo Users for 1-Click Role-Based Authentication
DEMO_USERS: Dict[str, UserProfile] = {
    "student@college.edu": UserProfile(
        id="usr-stud-01",
        name="Aarav Sharma",
        role="STUDENT",
        email="student@college.edu",
        department="Computer Science & Engineering",
        roll_or_staff_id="21CS042",
        title="Student (Year 4, B.Tech CSE)",
        avatar_url="🎓"
    ),
    "aarav.sharma@college.edu": UserProfile(
        id="usr-stud-01",
        name="Aarav Sharma",
        role="STUDENT",
        email="aarav.sharma@college.edu",
        department="Computer Science & Engineering",
        roll_or_staff_id="21CS042",
        title="Student (Year 4, B.Tech CSE)",
        avatar_url="🎓"
    ),
    "faculty@college.edu": UserProfile(
        id="usr-fac-01",
        name="Prof. Rajesh Verma",
        role="FACULTY",
        email="faculty@college.edu",
        department="Campus Facilities & Lab Superintendent",
        roll_or_staff_id="FAC-881",
        title="Associate Professor & Campus Technical Superintendent",
        avatar_url="👨‍🏫"
    ),
    "prof.verma@college.edu": UserProfile(
        id="usr-fac-01",
        name="Prof. Rajesh Verma",
        role="FACULTY",
        email="prof.verma@college.edu",
        department="Campus Facilities & Lab Superintendent",
        roll_or_staff_id="FAC-881",
        title="Associate Professor & Campus Technical Superintendent",
        avatar_url="👨‍🏫"
    ),
    "hod@college.edu": UserProfile(
        id="usr-hod-01",
        name="Dr. Ananya Shukla",
        role="HOD_ADMIN",
        email="hod@college.edu",
        department="Computer Science & Engineering",
        roll_or_staff_id="HOD-101",
        title="Head of Department (CSE) & Campus Dean of Infrastructure",
        avatar_url="🏛️"
    ),
    "hod.shukla@college.edu": UserProfile(
        id="usr-hod-01",
        name="Dr. Ananya Shukla",
        role="HOD_ADMIN",
        email="hod.shukla@college.edu",
        department="Computer Science & Engineering",
        roll_or_staff_id="HOD-101",
        title="Head of Department (CSE) & Campus Dean of Infrastructure",
        avatar_url="🏛️"
    )
}

class Database:
    def __init__(self):
        self.complaints: Dict[str, Complaint] = {}
        self.master_incidents: Dict[str, MasterIncident] = {}
        self.faculty_scorecards: Dict[str, FacultyScorecard] = {}
        self._seed_initial_data()
        self.recompute_rankings()

    def _seed_initial_data(self):
        now = datetime.utcnow()

        # Seed 1: The Sparking Wire near Examination Hall (CRITICAL - Rank #1)
        c1_id = "CMP-7001"
        c1_lat, c1_lng = 37.7753, -122.4190  # 57 meters from Oakridge / Campus Exam Hall!
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
            title="Active Arc-Flashing Electrical Conduit Outside Examination Hall Complex",
            description="Exposed 4.8kV utility conduit detached from ceiling and is violently sparking outside Hall Complex A. Semester final exam bell about to ring in 25 minutes.",
            original_transcript="Bhaiya yahan Oakridge school ke theek samne transformer se bohot tez sparks nikal rahe hain! Bachhe chutti hone pe nikalne wale hain, kisi ko current lag sakta hai, please turant kisi ko bhejo!",
            dialect="Urban North Indian / Hinglish Colloquial",
            translated_english="Brothers, right in front of Oakridge School, intense sparks are flying from the transformer! Kids are about to leave for recess, someone could get electrocuted, please send someone immediately!",
            category="Public Safety & Electrical",
            sub_tags=["High-Voltage Hazard", "Fire Risk", "Arc Flash Hazard", "Student Examination Zone"],
            sub_tag_confidences={"High-Voltage Hazard": 0.98, "Fire Risk": 0.91, "Student Examination Zone": 0.95},
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
            rank=1,
            score_breakdown=c1_score,
            status="IN_PROGRESS",
            user_name="Aarav Sharma",
            user_phone="+1 (555) 948-2104",
            student_roll="21CS042",
            student_email="aarav.sharma@college.edu",
            department="Computer Science & Engineering",
            block_or_hostel="Complex A Examination Hall Frontage",
            channel="PHONE_VOICE",
            location_name="Oakridge School & Campus Main Examination Hall",
            latitude=c1_lat,
            longitude=c1_lng,
            proof_type="PHOTO",
            image_url="/static/images/sparking_wire.svg",
            assigned_faculty_id="FAC-881",
            assigned_faculty_name="Prof. Rajesh Verma",
            created_at=(now - timedelta(minutes=48)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            sla_due_at=(now + timedelta(minutes=72)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            sla_seconds_remaining=4320,
            sla_escalated=False,
            hod_status="PENDING_REVIEW",
            audit_trail=[
                AuditLogEntry(
                    timestamp=(now - timedelta(minutes=48)).strftime("%H:%M:%S"),
                    event="STUDENT_GRIEVANCE_FILED",
                    actor="Student Aarav Sharma (21CS042)",
                    details="Audio distress parsed (92% panic). Visual hazard tagged 94/100. Proximity to Exam Hall Complex triggered Vulnerability Boost (+19.4pts)."
                ),
                AuditLogEntry(
                    timestamp=(now - timedelta(minutes=38)).strftime("%H:%M:%S"),
                    event="FACULTY_DISPATCHED",
                    actor="System Automation",
                    details="Assigned to Prof. Rajesh Verma (Campus Technical Superintendent). Insulated boom unit on-site."
                )
            ]
        )

        # Seed 2: Girls Hostel Water Failure (HIGH - Rank #2)
        c4_id = "CMP-7004"
        c4_lat, c4_lng = 37.7712, -122.4115  # Near Girls Hostel Block 3
        c4_score = priority_engine.calculate_priority(
            nlp_urgency=86.0,
            vision_hazard=78.0,
            cluster_size=2,
            lat=c4_lat,
            lng=c4_lng,
            vocal_panic_score=84.0
        )
        self.complaints[c4_id] = Complaint(
            id=c4_id,
            tracking_number="CMP-7004",
            title="Total Water Supply Failure on 2nd & 3rd Floors of Girls Hostel Block 3",
            description="Motor pump coupling failure. 180 resident students have zero running water since 6:00 AM before semester practical exam batches.",
            original_transcript="Bhaiya Block 3 Girls Hostel mein subah se paani bilkul nahi aa raha hai! Exams start hone wale hain, please turant motor check karo!",
            dialect="Urban Hinglish Colloquial",
            translated_english="Brothers, in Block 3 Girls Hostel there is no water since morning! Exams are starting soon, please check the motor pump immediately!",
            category="Hostel Living & Sanitation",
            sub_tags=["Hostel Water Outage", "Public Health", "180 Students Impacted"],
            sub_tag_confidences={"Hostel Water Outage": 0.97, "Public Health": 0.89},
            sentiment="Extreme Distress",
            vocal_emotion="Panicked",
            vocal_panic_score=84.0,
            visual_defect="High-Pressure Water Pump Cavitation & Riser Pipe Rupture",
            visual_hazard_score=78.0,
            nlp_urgency_score=86.0,
            cluster_size=2,
            context_risk_score=c4_score.context_score,
            priority_score=c4_score.total_score,
            priority_tier=c4_score.tier,
            rank=2,
            score_breakdown=c4_score,
            status="IN_PROGRESS",
            user_name="Priya Nair",
            user_phone="+1 (555) 819-3321",
            student_roll="22EC081",
            student_email="priya.nair@college.edu",
            department="Electronics & Communication",
            block_or_hostel="Girls Hostel Block 3 (Rooms 201-340)",
            channel="WEB",
            location_name="Girls Hostel Block 3 & Dining Wing",
            latitude=c4_lat,
            longitude=c4_lng,
            proof_type="PHOTO",
            image_url="/static/images/sparking_wire.svg",
            assigned_faculty_id="FAC-882",
            assigned_faculty_name="Er. Ramesh Kumar (Hostel Supervisor)",
            created_at=(now - timedelta(hours=1, minutes=20)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            sla_due_at=(now + timedelta(hours=2, minutes=40)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            sla_seconds_remaining=9600,
            sla_escalated=False,
            hod_status="PENDING_REVIEW",
            audit_trail=[
                AuditLogEntry(
                    timestamp=(now - timedelta(hours=1, minutes=20)).strftime("%H:%M:%S"),
                    event="STUDENT_GRIEVANCE_FILED",
                    actor="Student Priya Nair (22EC081)",
                    details="Hostel water shortage registered. Crowd volume multiplier boosted priority to Rank #2."
                )
            ]
        )

        # Seed 3: Campus Road Pothole (MEDIUM - Rank #3)
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
            title="Severe 8-Inch Asphalt Crater on Campus Bicycle Track",
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
            rank=3,
            score_breakdown=c2_score,
            status="IN_PROGRESS",
            user_name="Marcus Vance",
            user_phone="+1 (555) 302-8841",
            student_roll="23ME019",
            student_email="marcus.vance@college.edu",
            department="Mechanical Engineering",
            block_or_hostel="North Campus Bicycle Perimeter",
            channel="WEB",
            location_name="4th St & Bryant Ave (Northbound)",
            latitude=c2_lat,
            longitude=c2_lng,
            proof_type="PHOTO",
            image_url="/static/images/pothole.svg",
            assigned_faculty_id="FAC-882",
            assigned_faculty_name="Er. Ramesh Kumar",
            created_at=(now - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            sla_due_at=(now + timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            sla_seconds_remaining=14400,
            sla_escalated=False,
            hod_status="PENDING_REVIEW",
            audit_trail=[
                AuditLogEntry(
                    timestamp=(now - timedelta(hours=2)).strftime("%H:%M:%S"),
                    event="INTAKE_CLASSIFIED",
                    actor="Campus Facilities AI",
                    details="Surface cavity classified. Work order created for Campus Civil Works."
                )
            ]
        )

        # Seed 4: Duplicate Exam Fee Deduction (LOW - Rank #4, Auto-Resolver)
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
            title="Duplicate Semester Examination Fee Deducted on Student Portal ($89.00 / ₹7,200)",
            description="I was charged twice on October 28th for my semester end exam registration fee on ERP Invoice INV-402 ($89.00 x 2). Student Account #ACC-88321.",
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
            rank=4,
            score_breakdown=c3_score,
            status="TRIAGED",
            user_name="Elena Rostova",
            user_phone="+1 (555) 714-9923",
            student_roll="21CS104",
            student_email="elena.rostova@college.edu",
            department="Computer Science & Engineering",
            block_or_hostel="Administrative Block / Accounts Portal",
            channel="WEB",
            location_name="Account Portal / Digital Ingestion",
            latitude=37.7749,
            longitude=-122.4194,
            proof_type="PHOTO",
            image_url="/static/images/billing.svg",
            created_at=(now - timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            sla_due_at=(now + timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            sla_seconds_remaining=85500,
            sla_escalated=False,
            auto_resolved=False,
            hod_status="PENDING_REVIEW",
            audit_trail=[
                AuditLogEntry(
                    timestamp=(now - timedelta(minutes=15)).strftime("%H:%M:%S"),
                    event="ZERO_TOUCH_ELIGIBLE",
                    actor="Agentic Classifier",
                    details="Identified as Tier-1 digital invoice discrepancy. Ready for autonomous tool execution."
                )
            ]
        )

        # Seed 5: Already Solved Problem (Target for HOD Review & Work Quality Audit)
        c5_id = "CMP-7005"
        c5_lat, c5_lng = 37.7650, -122.4300
        c5_score = priority_engine.calculate_priority(
            nlp_urgency=88.0,
            vision_hazard=85.0,
            cluster_size=1,
            lat=c5_lat,
            lng=c5_lng,
            vocal_panic_score=80.0
        )
        self.complaints[c5_id] = Complaint(
            id=c5_id,
            tracking_number="CMP-7005",
            title="CS Lab 4 Main Compiler Server & Power Trip Ahead of 2 PM Practical Exam",
            description="Power supply surge tripped primary server rack in CS Lab 4. 18 student workstations powered down right before practical evaluation.",
            category="Academic Facilities & Labs",
            sub_tags=["CS Lab Failure", "Exam Disruption", "Server Tripped"],
            sub_tag_confidences={"CS Lab Failure": 0.99, "Exam Disruption": 0.96},
            sentiment="Distressed",
            vocal_emotion="Panicked",
            vocal_panic_score=80.0,
            visual_defect="Server Rack Power Supply Unit Failure & Tripped Breaker",
            visual_hazard_score=85.0,
            nlp_urgency_score=88.0,
            cluster_size=1,
            context_risk_score=c5_score.context_score,
            priority_score=c5_score.total_score,
            priority_tier=c5_score.tier,
            rank=5,
            score_breakdown=c5_score,
            status="VERIFIED_CLOSED",
            user_name="Rohan Mehta",
            user_phone="+1 (555) 431-8890",
            student_roll="21CS089",
            student_email="rohan.mehta@college.edu",
            department="Computer Science & Engineering",
            block_or_hostel="Computer Science Lab Complex (Lab 4)",
            channel="WEB",
            location_name="Computer Science Lab Complex & Server Rack",
            latitude=c5_lat,
            longitude=c5_lng,
            proof_type="PHOTO",
            image_url="/static/images/sparking_wire.svg",
            after_image_url="/static/images/repaired_wire.svg",
            assigned_faculty_id="FAC-881",
            assigned_faculty_name="Prof. Rajesh Verma",
            time_taken_minutes=42,
            resolved_at=(now - timedelta(minutes=18)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            resolution_proof={
                "verified": True,
                "is_good_resolution": True,
                "quality_verdict": "GOOD_FIX_EXCELLENT",
                "quality_score": 97.8,
                "fix_confidence": 97.8,
                "reason": "EXCELLENT FIX: Power supply unit replaced, GPU diagnostic benchmark completed, all 18 workstations online.",
                "cryptographic_token": "CERT-VERIFIED-42A9B8F12C",
                "recommendation_for_hod": "EXCELLENT WORK: Quick turnaround before semester exam. Ready for HOD approval."
            },
            created_at=(now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            sla_due_at=(now + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            sla_seconds_remaining=3600,
            sla_escalated=False,
            hod_status="APPROVED_EXCELLENT",
            hod_feedback="Commended: Fast 42-minute turnaround prevented cancellation of the 2 PM compilers evaluation.",
            hod_reviewed_at=(now - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            audit_trail=[
                AuditLogEntry(
                    timestamp=(now - timedelta(hours=1)).strftime("%H:%M:%S"),
                    event="STUDENT_REPORT_FILED",
                    actor="Rohan Mehta (21CS089)",
                    details="CS Lab 4 server outage reported with photo proof."
                ),
                AuditLogEntry(
                    timestamp=(now - timedelta(minutes=18)).strftime("%H:%M:%S"),
                    event="PROOF_OF_RESOLUTION_VERIFIED",
                    actor="Prof. Rajesh Verma & AI Guard",
                    details="AI Proof Scan: GOOD FIX (97.8% Quality). Token: CERT-VERIFIED-42A9B8F12C."
                ),
                AuditLogEntry(
                    timestamp=(now - timedelta(minutes=10)).strftime("%H:%M:%S"),
                    event="HOD_ENDORSEMENT_APPROVED",
                    actor="Dr. Ananya Shukla (HOD CSE)",
                    details="Approved with Commendation. Time taken: 42 minutes."
                )
            ]
        )

        # Seed 6: Water Main Master Incident (Existing cluster)
        m1_id = "MASTER-INC-202"
        m1_lat, m1_lng = 37.7830, -122.4160
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

        # Seed Faculty Performance Scorecards for HOD / Admin Review
        self.faculty_scorecards = {
            "FAC-881": FacultyScorecard(
                faculty_id="FAC-881",
                name="Prof. Rajesh Verma",
                role_title="Campus Technical Superintendent & Lab Head",
                department="Computer Science & Campus Facilities",
                tasks_assigned=16,
                tasks_resolved=15,
                avg_time_taken_hours=1.8,
                avg_quality_score=97.2,
                good_fixes_count=14,
                bad_fixes_count=1,
                rating=4.9
            ),
            "FAC-882": FacultyScorecard(
                faculty_id="FAC-882",
                name="Er. Ramesh Kumar",
                role_title="Senior Facilities & Hostel Maintenance Engineer",
                department="Civil & Hostel Works",
                tasks_assigned=24,
                tasks_resolved=21,
                avg_time_taken_hours=2.6,
                avg_quality_score=93.8,
                good_fixes_count=19,
                bad_fixes_count=2,
                rating=4.7
            ),
            "FAC-883": FacultyScorecard(
                faculty_id="FAC-883",
                name="Dr. Sunita Patil",
                role_title="Campus Health & Sanitation Officer",
                department="Mess & Student Welfare",
                tasks_assigned=11,
                tasks_resolved=11,
                avg_time_taken_hours=1.2,
                avg_quality_score=98.5,
                good_fixes_count=11,
                bad_fixes_count=0,
                rating=5.0
            )
        }

    def recompute_rankings(self):
        """
        Recalculates AI rankings for all complaints:
        Highest priority score = Rank #1, Rank #2, etc.
        """
        sorted_complaints = sorted(
            self.complaints.values(),
            key=lambda c: (0 if c.status == "VERIFIED_CLOSED" else 1, c.priority_score),
            reverse=True
        )
        for idx, c in enumerate(sorted_complaints):
            c.rank = idx + 1

    def get_all_complaints(self) -> List[Complaint]:
        self.recompute_rankings()
        return sorted(list(self.complaints.values()), key=lambda c: c.priority_score, reverse=True)

    def get_ranked_complaints(self) -> List[Complaint]:
        self.recompute_rankings()
        return sorted(list(self.complaints.values()), key=lambda c: c.rank)

    def get_student_complaints(self, student_email: str) -> List[Complaint]:
        self.recompute_rankings()
        return [c for c in self.complaints.values() if c.student_email == student_email or student_email in c.user_name.lower()]

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
                (c.student_roll and q in c.student_roll.lower()) or
                (c.student_email and q in c.student_email.lower()) or
                q in c.title.lower() or 
                q in c.location_name.lower() or
                q in c.category.lower()):
                results.append(c)
        return sorted(results, key=lambda x: x.priority_score, reverse=True)

    def save_complaint(self, complaint: Complaint):
        self.complaints[complaint.id] = complaint
        self.recompute_rankings()

    def get_all_masters(self) -> List[MasterIncident]:
        return sorted(list(self.master_incidents.values()), key=lambda m: m.priority_score, reverse=True)

    def get_master(self, master_id: str) -> Optional[MasterIncident]:
        return self.master_incidents.get(master_id)

    def get_faculty_scorecards(self) -> List[FacultyScorecard]:
        return list(self.faculty_scorecards.values())

    def review_hod_work(self, complaint_id: str, endorsement: str, feedback: str, hod_name: str) -> Dict[str, Any]:
        """HOD reviews completed work, reviews turnaround time, and endorses or requests rework."""
        c = self.get_complaint(complaint_id)
        if not c:
            return {"success": False, "message": "Complaint not found"}

        now = datetime.utcnow()
        c.hod_status = endorsement
        c.hod_feedback = feedback
        c.hod_reviewed_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        if endorsement == "REJECTED_REWORK":
            c.status = "IN_PROGRESS"
            event_name = "HOD_REJECTED_REWORK_REQUESTED"
        else:
            event_name = f"HOD_WORK_REVIEW_{endorsement}"

        c.audit_trail.append(AuditLogEntry(
            timestamp=now.strftime("%H:%M:%S"),
            event=event_name,
            actor=hod_name,
            details=f"Review decision: {endorsement}. Feedback: {feedback}"
        ))
        self.save_complaint(c)
        return {"success": True, "complaint": c.dict(), "message": f"HOD review recorded: {endorsement}"}

    def simulate_mass_outage(self) -> Dict[str, Any]:
        now = datetime.utcnow()
        master_id = f"MASTER-OUTAGE-{int(time.time())}"
        center_lat = 37.7650
        center_lng = -122.4300
        location_name = "Campus Power Substation & Lab Complex"

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
                rank=1,
                score_breakdown=score_res,
                status="TRIAGED",
                master_incident_id=master_id,
                is_master=False,
                user_name=name,
                user_phone=f"+1 (555) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
                student_roll=f"23CS{100 + i}",
                student_email=f"student{i+1}@college.edu",
                department="Engineering",
                block_or_hostel=location_name,
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
            priority_score=master_score.total_score,
            priority_tier="CRITICAL",
            status="ACTIVE",
            created_at=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            updated_at=now.strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        self.master_incidents[master_id] = master_incident
        self.recompute_rankings()

        return {
            "success": True,
            "master_incident": master_incident.dict(),
            "complaints_created_count": len(generated_complaint_ids),
            "swarmed_ids": generated_complaint_ids[:5],
            "message": f"Successfully simulated 25 concurrent complaints in Sector 4! Deduplicated into 1 Master Incident with priority boosted to {master_score.total_score}/100 [CRITICAL]."
        }

db = Database()
