import pytest
from backend.models import (
    LoginRequest,
    ComplaintSubmission,
    AntiFakeProofRequest,
    HODReviewRequest,
    Complaint
)
from backend.main import (
    get_demo_users,
    login_user,
    get_student_complaints,
    get_faculty_ranked_complaints,
    get_hod_overview
)
from backend.database import db, DEMO_USERS
from backend.ai.anti_fake_closure import anti_fake_guard
from backend.ai.priority_engine import priority_engine

def test_auth_demo_users_and_login():
    """Verify 1-click authentication and role-based login for all 3 portals."""
    users = get_demo_users()
    assert len(users) >= 3
    roles = {u.role for u in users}
    assert "STUDENT" in roles
    assert "FACULTY" in roles
    assert "HOD_ADMIN" in roles

    stud_login = login_user(LoginRequest(email="student@college.edu", role="STUDENT"))
    assert stud_login.user.role == "STUDENT"
    assert "tok_student" in stud_login.token
    assert stud_login.user.roll_or_staff_id == "21CS042"

    fac_login = login_user(LoginRequest(email="faculty@college.edu", role="FACULTY"))
    assert fac_login.user.role == "FACULTY"
    assert "tok_faculty" in fac_login.token
    assert fac_login.user.roll_or_staff_id == "FAC-881"

    hod_login = login_user(LoginRequest(email="hod@college.edu", role="HOD_ADMIN"))
    assert hod_login.user.role == "HOD_ADMIN"
    assert "tok_hod_admin" in hod_login.token
    assert hod_login.user.roll_or_staff_id == "HOD-101"

def test_student_complaint_intake_with_video_or_photo():
    """Verify student filing complaint with video or photo proof, department, and roll number."""
    c_id = "CMP-TEST-STUDENT"
    c = Complaint(
        id=c_id,
        tracking_number=c_id,
        title="Broken High-Speed Switch in Embedded Systems Lab",
        description="The Cisco 48-port switch in Room 204 keeps rebooting during lab practicals. Sparks seen near power port.",
        category="Public Safety & Electrical",
        user_name="Aarav Sharma",
        user_phone="+1 555-019-2834",
        student_roll="21CS042",
        student_email="student@college.edu",
        department="Computer Science & Engineering",
        block_or_hostel="CS Lab Building 2nd Floor",
        location_name="Embedded Systems Lab 204",
        latitude=37.7760,
        longitude=-122.4185,
        proof_type="VIDEO",
        video_url="/uploads/video_test_lab.mp4",
        image_url="/static/images/sparking_wire.svg",
        priority_score=88.5,
        priority_tier="CRITICAL",
        status="TRIAGED",
        created_at="2026-11-10T12:00:00Z",
        sla_due_at="2026-11-10T14:00:00Z",
        sla_seconds_remaining=7200
    )
    db.save_complaint(c)
    retrieved = db.get_complaint(c_id)
    assert retrieved is not None
    assert retrieved.proof_type == "VIDEO"
    assert retrieved.video_url == "/uploads/video_test_lab.mp4"
    assert retrieved.student_roll == "21CS042"
    assert retrieved.student_email == "student@college.edu"

    # Verify student portal filtering
    my_complaints = get_student_complaints("student@college.edu")
    assert any(item.id == c_id for item in my_complaints)

def test_faculty_scans_and_ranks_complaints():
    """Verify faculty portal receives complaints with AI priority score and global rankings (#1, #2, ...)."""
    complaints = get_faculty_ranked_complaints()
    assert len(complaints) >= 4
    ranks = [c.rank for c in complaints]
    assert ranks[0] == 1
    assert ranks[1] == 2
    # Ranked complaints should be ordered properly
    assert complaints[0].priority_score >= complaints[1].priority_score

def test_faculty_submits_proof_good_fix_evaluated():
    """Verify AI scans faculty proof and evaluates a GOOD FIX with high quality score."""
    complaint = db.get_complaint("CMP-7001")
    assert complaint is not None
    res = anti_fake_guard.evaluate_proof(
        complaint=complaint.dict(),
        after_preset="genuine_repaired_wire",
        resolver_notes="Conduit replaced with armored fire-retardant casing, ground insulation certified."
    )
    assert res.is_good_resolution is True
    assert res.quality_verdict == "GOOD_FIX_EXCELLENT"
    assert res.quality_score >= 95.0
    assert "EXCELLENT" in res.reason

def test_faculty_submits_proof_bad_fix_rejected():
    """Verify AI scans faculty proof and rejects a BAD/POOR FIX (e.g. tape patch or unrelated photo)."""
    complaint = db.get_complaint("CMP-7004")
    assert complaint is not None
    res = anti_fake_guard.evaluate_proof(
        complaint=complaint.dict(),
        after_preset="college_bad_tape_patch",
        resolver_notes="Put some tape around the leak temporarily."
    )
    assert res.is_good_resolution is False
    assert "BAD_FIX" in res.quality_verdict
    assert res.quality_score <= 35.0
    assert "SUB-STANDARD" in res.reason or "POOR" in res.reason

def test_hod_admin_overview_and_review_workflow():
    """Verify Admin/HOD overview (turnaround time, faculty scorecards) and work review."""
    overview = get_hod_overview()
    assert "total_grievances" in overview
    assert "avg_turnaround_minutes" in overview
    assert "avg_turnaround_display" in overview
    assert len(overview["scorecards"]) >= 3
    first_scorecard = overview["scorecards"][0]
    assert hasattr(first_scorecard, "faculty_id") or "faculty_id" in first_scorecard

    # HOD Review & Endorsement
    rev_data = db.review_hod_work(
        complaint_id="CMP-7005",
        endorsement="APPROVED_EXCELLENT",
        feedback="Outstanding work by Prof. Verma in restoring the CS Lab server before practical exams.",
        hod_name="Dr. Ananya Shukla (HOD CSE)"
    )
    assert rev_data["success"] is True
    assert rev_data["complaint"]["hod_status"] == "APPROVED_EXCELLENT"
    assert rev_data["complaint"]["hod_feedback"] is not None
