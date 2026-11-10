from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime

class ScoreBreakdown(BaseModel):
    nlp_score: float = Field(..., description="NLP text and urgency score (0-100)")
    vision_score: float = Field(..., description="Computer vision hazard score (0-100)")
    cluster_score: float = Field(..., description="Logarithmic crowd swarm multiplier score (0-100)")
    context_score: float = Field(..., description="GIS environmental proximity & vulnerability score (0-100)")
    weighted_nlp: float
    weighted_vision: float
    weighted_cluster: float
    weighted_context: float
    total_score: float = Field(..., description="Calibrated priority index (0-100)")
    tier: str = Field(..., description="CRITICAL, HIGH, MEDIUM, LOW")
    formula_str: str
    explanation: str
    nearby_critical_landmark: Optional[str] = None
    distance_to_landmark_meters: Optional[float] = None

class AudioAnalysisResult(BaseModel):
    transcript: str
    detected_language: str
    dialect: str
    translated_english: str
    acoustic_panic_score: float = Field(..., description="Distress/panic level 0-100")
    vocal_emotion: str = Field(..., description="Panicked, Angry, Frustrated, Calm")
    urgency_keywords: List[str] = Field(default_factory=list)

class VisionAnalysisResult(BaseModel):
    defect_detected: str
    hazard_score: float = Field(..., description="Hazard severity 0-100")
    hazard_level: str
    bounding_box: Optional[Dict[str, float]] = None
    detected_elements: List[str] = Field(default_factory=list)

class UserProfile(BaseModel):
    id: str
    name: str
    role: str  # STUDENT, FACULTY, HOD_ADMIN
    email: str
    department: str
    roll_or_staff_id: str
    title: Optional[str] = None
    avatar_url: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: Optional[str] = "password"
    role: Optional[str] = None

class LoginResponse(BaseModel):
    token: str
    user: UserProfile

class ComplaintSubmission(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    voice_audio_base64: Optional[str] = None
    voice_audio_preset: Optional[str] = None
    image_base64: Optional[str] = None
    image_preset: Optional[str] = None
    proof_type: str = "PHOTO"  # PHOTO, VIDEO, AUDIO
    video_base64: Optional[str] = None
    channel: str = "WEB"  # WEB, WHATSAPP, EMAIL, PHONE_VOICE
    user_name: str = "Aarav Sharma"
    user_phone: Optional[str] = "+1 (555) 019-2834"
    student_roll: Optional[str] = "21CS042"
    student_email: Optional[str] = "aarav.sharma@college.edu"
    department: Optional[str] = "Computer Science & Engineering"
    block_or_hostel: Optional[str] = "Girls Hostel Block 3 / Complex A"
    latitude: float = 37.7749
    longitude: float = -122.4194
    location_name: str = "Complex A Examination Hall Frontage"

class AuditLogEntry(BaseModel):
    timestamp: str
    event: str
    actor: str
    details: str

class Complaint(BaseModel):
    id: str
    tracking_number: str
    title: str
    description: str
    original_transcript: Optional[str] = None
    dialect: Optional[str] = None
    translated_english: Optional[str] = None
    category: str
    sub_tags: List[str] = Field(default_factory=list)
    sub_tag_confidences: Dict[str, float] = Field(default_factory=dict)
    sentiment: str = "Negative"
    vocal_emotion: str = "Calm"
    vocal_panic_score: float = 0.0
    visual_defect: Optional[str] = None
    visual_hazard_score: float = 0.0
    nlp_urgency_score: float = 50.0
    cluster_size: int = 1
    context_risk_score: float = 20.0
    priority_score: float = 50.0
    priority_tier: str = "MEDIUM"
    rank: int = 1  # AI-assigned global ranking for faculty portal
    score_breakdown: Optional[ScoreBreakdown] = None
    status: str = "TRIAGED"  # TRIAGED, IN_PROGRESS, SOLVED_PENDING_REVIEW, VERIFIED_CLOSED, ESCALATED
    master_incident_id: Optional[str] = None
    is_master: bool = False
    user_name: str = "Student"
    user_phone: Optional[str] = None
    student_roll: Optional[str] = None
    student_email: Optional[str] = None
    department: Optional[str] = "Campus General"
    block_or_hostel: Optional[str] = "Campus Block"
    channel: str = "WEB"
    location_name: str
    latitude: float
    longitude: float
    proof_type: str = "PHOTO"
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    after_image_url: Optional[str] = None
    after_video_url: Optional[str] = None
    assigned_faculty_id: Optional[str] = None
    assigned_faculty_name: Optional[str] = None
    resolution_proof: Optional[Dict[str, Any]] = None
    auto_resolved: bool = False
    auto_resolution_details: Optional[Dict[str, Any]] = None
    created_at: str
    sla_due_at: str
    sla_seconds_remaining: int
    sla_escalated: bool = False
    resolved_at: Optional[str] = None
    time_taken_minutes: Optional[int] = None
    hod_status: str = "PENDING_REVIEW"  # PENDING_REVIEW, APPROVED_EXCELLENT, APPROVED_SATISFACTORY, REJECTED_REWORK
    hod_feedback: Optional[str] = None
    hod_reviewed_at: Optional[str] = None
    audit_trail: List[AuditLogEntry] = Field(default_factory=list)

class MasterIncident(BaseModel):
    id: str
    title: str
    category: str
    sub_tag: str
    complaint_count: int
    complaint_ids: List[str]
    center_latitude: float
    center_longitude: float
    location_name: str
    hazard_level: str
    priority_score: float
    priority_tier: str
    status: str = "ACTIVE"
    created_at: str
    updated_at: str

class AntiFakeProofRequest(BaseModel):
    complaint_id: str
    after_image_base64: Optional[str] = None
    after_image_preset: Optional[str] = None
    after_video_base64: Optional[str] = None
    proof_type: str = "PHOTO"  # PHOTO, VIDEO
    resolver_id: str = "FAC-881"
    resolver_name: str = "Prof. Rajesh Verma"
    resolver_notes: str = "Completed scheduled on-site repair and test diagnostics."
    time_spent_minutes: int = 45
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class AntiFakeProofResponse(BaseModel):
    verified: bool
    is_good_resolution: bool  # True = GOOD FIX, False = BAD FIX
    quality_verdict: str  # GOOD_FIX_EXCELLENT, GOOD_FIX_SATISFACTORY, BAD_FIX_INCOMPLETE, BAD_FIX_UNRELATED
    quality_score: float  # 0 to 100%
    fix_confidence: float
    scene_similarity_score: float
    defect_remediation_score: float
    reason: str
    visual_diff_highlights: str
    recommendation_for_hod: str
    cryptographic_token: Optional[str] = None
    timestamp: str

class FacultyScorecard(BaseModel):
    faculty_id: str
    name: str
    role_title: str
    department: str
    tasks_assigned: int
    tasks_resolved: int
    avg_time_taken_hours: float
    avg_quality_score: float
    good_fixes_count: int
    bad_fixes_count: int
    rating: float  # out of 5.0

class HODReviewRequest(BaseModel):
    complaint_id: str
    endorsement: str  # APPROVED_EXCELLENT, APPROVED_SATISFACTORY, REJECTED_REWORK
    feedback: str
    hod_name: str = "Dr. Ananya Shukla (HOD CSE & Campus Dean)"

class ZeroTouchRequest(BaseModel):
    complaint_id: str

class ZeroTouchResponse(BaseModel):
    success: bool
    execution_time_seconds: float
    actions_taken: List[Dict[str, Any]]
    refund_transaction_id: Optional[str] = None
    message: str

class CopilotDraftRequest(BaseModel):
    complaint_id: str
    tone: str = "EMPATHETIC"  # EMPATHETIC, FORMAL, ACTION_ORIENTED

class CopilotDraftResponse(BaseModel):
    complaint_id: str
    user_emotion: str
    draft_message: str
    policy_citations: List[str]
    recommended_actions: List[str]

class ForecastingAlert(BaseModel):
    id: str
    headline: str
    category: str
    location_zone: str
    probability: float
    historical_velocity_spike: str
    predicted_impact: str
    recommended_action: str
    severity: str
    timestamp: str
    dispatched: bool = False

class OllamaConfigUpdate(BaseModel):
    base_url: str
    model: str
