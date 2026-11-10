import os
import time
import json
import base64
import asyncio
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.models import (
    ComplaintSubmission,
    Complaint,
    AntiFakeProofRequest,
    AntiFakeProofResponse,
    ZeroTouchRequest,
    ZeroTouchResponse,
    CopilotDraftRequest,
    CopilotDraftResponse,
    OllamaConfigUpdate,
    AuditLogEntry,
    UserProfile,
    LoginRequest,
    LoginResponse,
    FacultyScorecard,
    HODReviewRequest
)
from backend.database import db, DEMO_USERS
from backend.ai.ollama_client import ollama_client
from backend.ai.multimodal_triage import multimodal_triage
from backend.ai.priority_engine import priority_engine
from backend.ai.clustering import swarm_clustering
from backend.ai.anti_fake_closure import anti_fake_guard
from backend.ai.zero_touch_resolver import zero_touch_resolver
from backend.ai.copilot import empathy_copilot
from backend.ai.forecasting import failure_forecasting

app = FastAPI(
    title="ComplainAI API",
    description="Autonomous Multimodal Grievance Intelligence & Zero-Touch Resolution Ecosystem",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

import sys

ticker_running = True

# Background task for live SLA countdown updates & auto-escalation
async def sla_ticker_loop():
    while ticker_running:
        try:
            now = datetime.utcnow()
            for c in list(db.complaints.values()):
                if c.status in ["TRIAGED", "IN_PROGRESS"]:
                    try:
                        due = datetime.strptime(c.sla_due_at, "%Y-%m-%dT%H:%M:%SZ")
                        delta = (due - now).total_seconds()
                        c.sla_seconds_remaining = int(delta)
                        if delta <= 0 and not c.sla_escalated:
                            c.sla_escalated = True
                            c.status = "ESCALATED"
                            c.audit_trail.append(AuditLogEntry(
                                timestamp=now.strftime("%H:%M:%S"),
                                event="SLA_BREACH_ESCALATION",
                                actor="Automated SLA Matrix",
                                details="SLA timer expired. Automatically escalated to Senior Municipal Supervisor & Department Head."
                            ))
                            await manager.broadcast({
                                "event": "SLA_ESCALATION",
                                "complaint_id": c.id,
                                "tracking_number": c.tracking_number,
                                "priority_tier": c.priority_tier
                            })
                    except Exception:
                        pass
        except Exception:
            pass
        try:
            await asyncio.sleep(5)
        except asyncio.CancelledError:
            break

@app.on_event("startup")
async def startup_event():
    if "pytest" in sys.modules:
        return
    asyncio.create_task(sla_ticker_loop())
    # Test initial Ollama connection
    await ollama_client.check_health()

@app.on_event("shutdown")
def shutdown_event():
    global ticker_running
    ticker_running = False

# WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial handshake state
        health = await ollama_client.check_health()
        await websocket.send_json({
            "event": "CONNECTED",
            "ollama_status": health,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        })
        while True:
            data = await websocket.receive_text()
            # keepalive or ping
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

# ----------------- REST ENDPOINTS -----------------

@app.get("/api/health")
async def get_health():
    """Returns Ollama status, connected models, and active engine configuration."""
    health = await ollama_client.check_health()
    return {
        "status": "online",
        "service": "ComplainAI Core Ecosystem",
        "ollama": health,
        "critical_landmarks_count": len(settings.CRITICAL_LANDMARKS),
        "total_complaints": len(db.complaints),
        "active_masters": len(db.master_incidents),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

@app.post("/api/ollama/config")
async def update_ollama_config(cfg: OllamaConfigUpdate):
    """Update Ollama base URL or active model from UI."""
    ollama_client.base_url = cfg.base_url.rstrip("/")
    ollama_client.model = cfg.model
    health = await ollama_client.check_health()
    return {"success": True, "updated_health": health}

# ----------------- AUTHENTICATION & ROLE MANAGEMENT -----------------

@app.get("/api/auth/demo-users")
def get_demo_users():
    """Return available demo accounts for 1-click login into Student, Faculty, or HOD/Admin portals."""
    unique_users = {}
    for email, user in DEMO_USERS.items():
        if user.email not in unique_users:
            unique_users[user.email] = user
    return list(unique_users.values())

@app.post("/api/auth/login", response_model=LoginResponse)
def login_user(req: LoginRequest):
    """Authenticate student, faculty/staff, or Admin/HOD."""
    email = req.email.strip().lower()
    user = DEMO_USERS.get(email)
    if not user:
        # Check by role fallback
        for u in DEMO_USERS.values():
            if req.role and u.role.upper() == req.role.upper():
                user = u
                break
    if not user:
        role = req.role.upper() if req.role else "STUDENT"
        user = UserProfile(
            id=f"usr-{int(time.time())}",
            name=email.split("@")[0].replace(".", " ").title() if "@" in email else email.title(),
            role=role,
            email=email,
            department="Computer Science & Engineering",
            roll_or_staff_id="21CS999" if role == "STUDENT" else ("FAC-999" if role == "FACULTY" else "HOD-999"),
            title=f"Campus {role.capitalize()}",
            avatar_url="🎓" if role == "STUDENT" else ("👨‍🏫" if role == "FACULTY" else "🏛️")
        )
        DEMO_USERS[email] = user

    token = f"tok_{user.role.lower()}_{uuid.uuid4().hex[:12]}"
    return LoginResponse(
        token=token,
        user=user,
        message=f"Logged in successfully as {user.name} ({user.title})"
    )

@app.get("/api/auth/me")
def get_current_user_profile(email: Optional[str] = None, role: Optional[str] = None):
    """Return user profile for an active session."""
    if email and email.lower() in DEMO_USERS:
        return DEMO_USERS[email.lower()]
    if role:
        for u in DEMO_USERS.values():
            if u.role.upper() == role.upper():
                return u
    # Default to student demo
    return DEMO_USERS["student@college.edu"]

# ----------------- STUDENT COMPLAINT SERVICES -----------------

@app.get("/api/student/my-complaints")
def get_student_complaints(email: Optional[str] = "student@college.edu"):
    """Fetch grievances submitted by the student, with live ranking, AI analysis & resolution proof."""
    target_email = email.strip().lower() if email else "student@college.edu"
    return db.get_student_complaints(target_email)

@app.get("/api/landmarks")
def get_landmarks():
    """Return critical infrastructure landmarks for live GIS map."""
    return settings.CRITICAL_LANDMARKS

@app.get("/api/complaints")
def list_complaints():
    """List all complaints with priority scores and status."""
    return db.get_all_complaints()

@app.get("/api/tracking/search")
def search_tracking(q: str = ""):
    """Search grievances by tracking number, ID, location, phone, or title."""
    return db.search_complaints(q)

@app.get("/api/complaints/{complaint_id}")
def get_complaint(complaint_id: str):
    complaint = db.get_complaint(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint

@app.post("/api/complaints/triage")
async def triage_complaint(sub: ComplaintSubmission):
    """
    Zero-Input "Snap & Speak" Multimodal Triage Endpoint.
    Transcribes audio, extracts vocal panic/emotion, scores visual hazard,
    applies dynamic priority formula with vulnerability boost,
    and deduplicates via swarm clustering.
    """
    now = datetime.utcnow()
    c_id = f"CMP-{random.randint(7050, 9999)}"

    # 1. Audio Processing & Vocal Emotion Extraction
    audio_res = multimodal_triage.analyze_audio(
        audio_base64=sub.voice_audio_base64,
        preset_key=sub.voice_audio_preset,
        raw_text=sub.description
    )

    # 2. Text Classification
    effective_text = sub.description or audio_res.translated_english or audio_res.transcript
    category, sub_tags, tag_confidences, nlp_urgency = multimodal_triage.classify_nlp_tags(effective_text)

    # 3. Computer Vision Hazard Scoring
    vision_res = multimodal_triage.analyze_vision(
        image_base64=sub.image_base64,
        preset_key=sub.image_preset,
        text_hint=effective_text
    )

    # 4. Swarm Clustering Check
    candidate = {
        "id": c_id,
        "category": category,
        "description": effective_text,
        "latitude": sub.latitude,
        "longitude": sub.longitude,
        "nlp_urgency_score": nlp_urgency,
        "visual_hazard_score": vision_res.hazard_score,
        "vocal_panic_score": audio_res.acoustic_panic_score
    }
    master_id, is_new_master, cluster_size = swarm_clustering.create_or_join_cluster(
        candidate,
        list(db.master_incidents.values())
    )

    # 5. Dynamic Priority Formula with Vulnerability Boost
    score_breakdown = priority_engine.calculate_priority(
        nlp_urgency=nlp_urgency,
        vision_hazard=vision_res.hazard_score,
        cluster_size=cluster_size,
        lat=sub.latitude,
        lng=sub.longitude,
        vocal_panic_score=audio_res.acoustic_panic_score
    )

    # 6. SLA Duration calculation
    duration_mins = settings.SLA_DURATIONS_MINUTES.get(score_breakdown.tier, 1440)
    sla_due = now + timedelta(minutes=duration_mins)

    # Video URL resolution if video proof uploaded
    video_url = None
    if sub.video_base64 and len(sub.video_base64) > 100:
        try:
            os.makedirs("backend/uploads", exist_ok=True)
            header, encoded = sub.video_base64.split(",", 1) if "," in sub.video_base64 else ("", sub.video_base64)
            ext = "mp4"
            if "webm" in header:
                ext = "webm"
            elif "mov" in header:
                ext = "mov"
            fname = f"video_{c_id}.{ext}"
            fpath = os.path.join("backend", "uploads", fname)
            with open(fpath, "wb") as f:
                f.write(base64.b64decode(encoded))
            video_url = f"/uploads/{fname}"
        except Exception:
            pass

    # Image URL resolution
    img_url = "/static/images/pothole.svg"
    if sub.image_base64 and len(sub.image_base64) > 100:
        try:
            os.makedirs("backend/uploads", exist_ok=True)
            header, encoded = sub.image_base64.split(",", 1) if "," in sub.image_base64 else ("", sub.image_base64)
            ext = "png"
            if "jpeg" in header or "jpg" in header:
                ext = "jpg"
            elif "webp" in header:
                ext = "webp"
            fname = f"upload_{c_id}.{ext}"
            fpath = os.path.join("backend", "uploads", fname)
            with open(fpath, "wb") as f:
                f.write(base64.b64decode(encoded))
            img_url = f"/uploads/{fname}"
        except Exception:
            pass
    elif sub.image_preset and f"{sub.image_preset}.svg" in os.listdir("backend/static/images"):
        img_url = f"/static/images/{sub.image_preset}.svg"
    elif "wire" in sub.image_preset if sub.image_preset else False or "spark" in effective_text.lower():
        img_url = "/static/images/sparking_wire.svg"
    elif "bill" in effective_text.lower() or "charge" in effective_text.lower():
        img_url = "/static/images/billing.svg"

    # 7. Create Complaint Entity
    complaint = Complaint(
        id=c_id,
        tracking_number=c_id,
        title=sub.title or f"{vision_res.defect_detected} ({sub.location_name})",
        description=effective_text,
        original_transcript=audio_res.transcript,
        dialect=audio_res.dialect,
        translated_english=audio_res.translated_english,
        category=category,
        sub_tags=sub_tags,
        sub_tag_confidences=tag_confidences,
        sentiment="Negative" if audio_res.acoustic_panic_score > 40 else "Neutral",
        vocal_emotion=audio_res.vocal_emotion,
        vocal_panic_score=audio_res.acoustic_panic_score,
        visual_defect=vision_res.defect_detected,
        visual_hazard_score=vision_res.hazard_score,
        nlp_urgency_score=nlp_urgency,
        cluster_size=cluster_size,
        context_risk_score=score_breakdown.context_score,
        priority_score=score_breakdown.total_score,
        priority_tier=score_breakdown.tier,
        score_breakdown=score_breakdown,
        status="TRIAGED",
        master_incident_id=master_id,
        is_master=False,
        user_name=sub.user_name,
        user_phone=sub.user_phone,
        student_roll=sub.student_roll or "21CS042",
        student_email=sub.student_email or "student@college.edu",
        department=sub.department or "Computer Science & Engineering",
        block_or_hostel=sub.block_or_hostel or sub.location_name,
        proof_type=sub.proof_type or ("VIDEO" if video_url else "PHOTO"),
        channel=sub.channel,
        location_name=sub.location_name,
        latitude=sub.latitude,
        longitude=sub.longitude,
        image_url=img_url,
        video_url=video_url,
        hod_status="PENDING_REVIEW",
        created_at=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        sla_due_at=sla_due.strftime("%Y-%m-%dT%H:%M:%SZ"),
        sla_seconds_remaining=duration_mins * 60,
        sla_escalated=False,
        audit_trail=[
            AuditLogEntry(
                timestamp=now.strftime("%H:%M:%S"),
                event="STUDENT_PROOF_TRIAGE",
                actor="ComplainAI Multimodal Engine (Ollama/CV)",
                details=f"Classified under '{category}'. Priority calibrated to {score_breakdown.total_score}/100 [{score_breakdown.tier}]. Proof format: {sub.proof_type or 'PHOTO'}."
            )
        ]
    )

    db.save_complaint(complaint)

    # Broadcast to live UI via WebSocket
    await manager.broadcast({
        "event": "NEW_COMPLAINT",
        "complaint": complaint.dict(),
        "cluster_size": cluster_size,
        "master_incident_id": master_id
    })

    return complaint

@app.get("/api/masters")
def list_masters():
    """List all Master Incidents."""
    return db.get_all_masters()

@app.post("/api/demo/simulate-mass-outage")
async def simulate_mass_outage():
    """
    Minute 2 Pitch Demonstration:
    Fires 25 citizen complaints in Sector 4 and auto-clusters into 1 pulsing Master Incident.
    """
    res = db.simulate_mass_outage()
    await manager.broadcast({
        "event": "MASS_OUTAGE_SIMULATED",
        "master_incident": res["master_incident"],
        "swarmed_count": res["complaints_created_count"]
    })
    return res

@app.post("/api/resolver/anti-fake-verify")
async def verify_proof_of_resolution(req: AntiFakeProofRequest):
    """
    Minute 3 Pitch Demonstration:
    Proof-of-Resolution 'Anti-Fake Closure' Guard.
    Compares Before vs After photo to prevent false closures.
    """
    complaint = db.get_complaint(req.complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    # Run CV Anti-Fake verification
    res = anti_fake_guard.evaluate_proof(
        complaint=complaint.dict(),
        after_preset=req.after_image_preset,
        after_image_base64=req.after_image_base64,
        resolver_notes=req.resolver_notes
    )

    now = datetime.utcnow()
    if res.verified:
        complaint.status = "VERIFIED_CLOSED"
        if req.after_image_base64 and len(req.after_image_base64) > 100:
            try:
                os.makedirs("backend/uploads", exist_ok=True)
                header, encoded = req.after_image_base64.split(",", 1) if "," in req.after_image_base64 else ("", req.after_image_base64)
                ext = "png"
                if "jpeg" in header or "jpg" in header:
                    ext = "jpg"
                elif "webp" in header:
                    ext = "webp"
                fname = f"after_{complaint.id}_{int(time.time())}.{ext}"
                fpath = os.path.join("backend", "uploads", fname)
                with open(fpath, "wb") as f:
                    f.write(base64.b64decode(encoded))
                complaint.after_image_url = f"/uploads/{fname}"
            except Exception:
                complaint.after_image_url = f"/static/images/{req.after_image_preset}.svg" if req.after_image_preset else "/static/images/repaired_pothole.svg"
        else:
            complaint.after_image_url = f"/static/images/{req.after_image_preset}.svg" if req.after_image_preset else "/static/images/repaired_pothole.svg"

        complaint.resolution_proof = res.dict()
        complaint.audit_trail.append(AuditLogEntry(
            timestamp=now.strftime("%H:%M:%S"),
            event="PROOF_OF_RESOLUTION_VERIFIED",
            actor=f"Resolver {req.resolver_id} & AI Guard",
            details=f"Photographic remediation verified ({res.fix_confidence}% confidence). Cryptographic token generated: {res.cryptographic_token}."
        ))
    else:
        complaint.audit_trail.append(AuditLogEntry(
            timestamp=now.strftime("%H:%M:%S"),
            event="FAKE_CLOSURE_ATTEMPT_REJECTED",
            actor="Anti-Fake Closure Guard (VLM)",
            details=f"REJECTED: {res.reason} (Fix Confidence: {res.fix_confidence}%)."
        ))

    db.save_complaint(complaint)

    await manager.broadcast({
        "event": "RESOLUTION_PROOF_EVALUATED",
        "complaint_id": complaint.id,
        "verified": res.verified,
        "status": complaint.status,
        "fix_confidence": res.fix_confidence,
        "reason": res.reason
    })

    return res

@app.post("/api/resolver/copilot-draft")
def generate_copilot_draft(req: CopilotDraftRequest):
    """Generate empathy-first de-escalation response for field/support agent."""
    complaint = db.get_complaint(req.complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return empathy_copilot.generate_draft(complaint.dict(), tone=req.tone)

@app.post("/api/resolver/zero-touch-execute")
async def execute_zero_touch(req: ZeroTouchRequest):
    """
    Agentic Zero-Touch Auto-Resolver Endpoint.
    Executes multi-tool autonomous resolution for digital/billing tickets in ~4 seconds.
    """
    complaint = db.get_complaint(req.complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    res = zero_touch_resolver.execute_resolution(complaint.dict())

    now = datetime.utcnow()
    complaint.status = "AUTO_RESOLVED"
    complaint.auto_resolved = True
    complaint.auto_resolution_details = res.dict()
    complaint.audit_trail.append(AuditLogEntry(
        timestamp=now.strftime("%H:%M:%S"),
        event="ZERO_TOUCH_AUTO_RESOLVED",
        actor="Agentic Tool-Calling Resolver",
        details=f"Resolved autonomously in {res.execution_time_seconds}s. Stripe Refund #{res.refund_transaction_id} issued."
    ))

    db.save_complaint(complaint)

    await manager.broadcast({
        "event": "ZERO_TOUCH_RESOLVED",
        "complaint_id": complaint.id,
        "execution_time": res.execution_time_seconds,
        "refund_id": res.refund_transaction_id
    })

    return res

@app.get("/api/forecasting/alerts")
def get_forecasting_alerts():
    """Return predictive root-cause & failure forecasting alerts."""
    return failure_forecasting.get_active_alerts()

@app.post("/api/forecasting/dispatch/{alert_id}")
async def dispatch_forecast_crew(alert_id: str):
    """Dispatch preventive maintenance crew before hardware blowout."""
    res = failure_forecasting.dispatch_preventative_crew(alert_id)
    await manager.broadcast({
        "event": "PREVENTIVE_CREW_DISPATCHED",
        "alert_id": alert_id
    })
    return res

# ----------------- FACULTY & STAFF RESOLUTION SERVICES -----------------

@app.get("/api/faculty/ranked-complaints")
def get_faculty_ranked_complaints():
    """
    Faculty Portal: AI scans all complaints submitted by students
    and gives an explainable priority score and global ranking (#1, #2, etc.).
    """
    return db.get_ranked_complaints()

@app.post("/api/faculty/submit-proof")
async def faculty_submit_proof(req: AntiFakeProofRequest):
    """
    Faculty submits resolution proof (photo or video).
    AI scans proof against the original problem and determines whether the fix is GOOD or BAD:
    Provides quality score (0-100%), quality verdict, and detailed explanation.
    """
    complaint = db.get_complaint(req.complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    res = anti_fake_guard.evaluate_proof(
        complaint=complaint.dict(),
        after_preset=req.after_image_preset,
        after_image_base64=req.after_image_base64,
        resolver_notes=req.resolver_notes
    )

    now = datetime.utcnow()
    created_dt = datetime.strptime(complaint.created_at, "%Y-%m-%dT%H:%M:%SZ")
    time_taken_mins = max(10, int((now - created_dt).total_seconds() / 60))

    if res.is_good_resolution:
        complaint.status = "VERIFIED_CLOSED"
        complaint.resolved_at = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        complaint.time_taken_minutes = time_taken_mins
        complaint.assigned_faculty_id = req.resolver_id or "FAC-881"
        complaint.assigned_faculty_name = "Prof. Rajesh Verma"
        complaint.hod_status = "PENDING_REVIEW"
    else:
        complaint.status = "IN_PROGRESS"
        complaint.hod_status = "REWORK_REQUIRED"

    # Store after photo/video if base64 provided
    if req.after_image_base64 and len(req.after_image_base64) > 100:
        try:
            os.makedirs("backend/uploads", exist_ok=True)
            header, encoded = req.after_image_base64.split(",", 1) if "," in req.after_image_base64 else ("", req.after_image_base64)
            ext = "png"
            if "jpeg" in header or "jpg" in header:
                ext = "jpg"
            elif "mp4" in header or "webm" in header:
                ext = "mp4"
            fname = f"proof_{complaint.id}_{int(time.time())}.{ext}"
            fpath = os.path.join("backend", "uploads", fname)
            with open(fpath, "wb") as f:
                f.write(base64.b64decode(encoded))
            complaint.after_image_url = f"/uploads/{fname}"
        except Exception:
            complaint.after_image_url = f"/static/images/{req.after_image_preset}.svg" if req.after_image_preset else "/static/images/repaired_pothole.svg"
    elif req.after_image_preset:
        complaint.after_image_url = f"/static/images/{req.after_image_preset}.svg"

    complaint.resolution_proof = res.dict()
    event_name = "FACULTY_PROOF_GOOD_FIX" if res.is_good_resolution else "FACULTY_PROOF_BAD_FIX_REJECTED"
    complaint.audit_trail.append(AuditLogEntry(
        timestamp=now.strftime("%H:%M:%S"),
        event=event_name,
        actor=f"Faculty ({complaint.assigned_faculty_name or 'Faculty Staff'}) & AI Guard",
        details=f"AI Quality Verdict: {res.quality_verdict} ({res.quality_score}%). {res.reason}"
    ))

    db.save_complaint(complaint)

    await manager.broadcast({
        "event": "FACULTY_PROOF_EVALUATED",
        "complaint_id": complaint.id,
        "is_good_resolution": res.is_good_resolution,
        "quality_score": res.quality_score,
        "quality_verdict": res.quality_verdict,
        "status": complaint.status,
        "time_taken_minutes": complaint.time_taken_minutes
    })

    return {
        "evaluation": res.dict(),
        "complaint": complaint.dict(),
        "is_good": res.is_good_resolution,
        "verdict": res.quality_verdict,
        "quality_score": res.quality_score
    }

# ----------------- ADMIN & HOD COMMAND SERVICES -----------------

@app.get("/api/hod/overview")
def get_hod_overview():
    """
    Admin/HOD Portal:
    - See all the work that happened across campus
    - How it happened, how much time was taken (in minutes/hours)
    - Review how good the work was done by faculty/staff members (quality ratings & scorecards)
    """
    complaints = db.get_all_complaints()
    resolved = [c for c in complaints if c.status in ["VERIFIED_CLOSED", "AUTO_RESOLVED"]]
    in_progress = [c for c in complaints if c.status in ["IN_PROGRESS", "TRIAGED", "ESCALATED"]]
    
    total_time_mins = sum(c.time_taken_minutes or 0 for c in resolved)
    avg_turnaround_mins = int(total_time_mins / len(resolved)) if resolved else 45

    cat_counts = {}
    for c in complaints:
        cat_counts[c.category] = cat_counts.get(c.category, 0) + 1

    return {
        "total_grievances": len(complaints),
        "resolved_count": len(resolved),
        "pending_count": len(in_progress),
        "avg_turnaround_minutes": avg_turnaround_mins,
        "avg_turnaround_display": f"{avg_turnaround_mins // 60}h {avg_turnaround_mins % 60}m" if avg_turnaround_mins >= 60 else f"{avg_turnaround_mins} mins",
        "scorecards": db.get_faculty_scorecards(),
        "category_breakdown": cat_counts,
        "recent_resolutions": [c.dict() for c in resolved[:10]],
        "work_history": [c.dict() for c in complaints]
    }

@app.post("/api/hod/review-work")
async def hod_review_work(req: HODReviewRequest):
    """
    Admin/HOD reviews faculty/staff work:
    Endorses (Approve/Commend) or Rejects (Rework Requested) with formal feedback.
    """
    res = db.review_hod_work(
        complaint_id=req.complaint_id,
        endorsement=req.endorsement,
        feedback=req.feedback,
        hod_name=req.hod_name
    )
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("message"))

    await manager.broadcast({
        "event": "HOD_REVIEW_COMPLETED",
        "complaint_id": req.complaint_id,
        "endorsement": req.endorsement,
        "feedback": req.feedback,
        "hod_name": req.hod_name
    })

    return res

# Ensure uploads folder exists and mount static directories
os.makedirs("backend/uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="backend/uploads"), name="uploads")
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join("backend", "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"message": "ComplainAI API is running. static/index.html is loading."})

if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
