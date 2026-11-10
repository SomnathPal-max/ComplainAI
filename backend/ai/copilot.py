from typing import Dict, Any, List
from backend.models import CopilotDraftResponse

class EmpathyCopilot:
    def __init__(self):
        pass

    def generate_draft(self, complaint: Dict[str, Any], tone: str = "EMPATHETIC") -> CopilotDraftResponse:
        """
        Generate tailored, empathetic de-escalation response based on emotional state.
        """
        emotion = complaint.get("vocal_emotion", "Frustrated")
        user_name = complaint.get("user_name", "Valued Citizen")
        category = complaint.get("category", "Grievance")
        tracking_num = complaint.get("tracking_number", "CMP-1001")
        landmark = complaint.get("score_breakdown", {}).get("nearby_critical_landmark")

        if emotion == "Panicked":
            draft = (
                f"Dear {user_name},\n\n"
                f"We hear how urgent and terrifying this situation is, especially given its location"
                + (f" near {landmark}" if landmark else "") + 
                f". Please step back and maintain a safe perimeter immediately—your safety and that of the neighborhood is our top priority.\n\n"
                f"Our Emergency Rapid Response Crew has already been dispatched with priority override (Ticket #{tracking_num}). "
                f"The supervisor on call has been alerted, and an on-site technician is en route with an estimated arrival within 15 minutes.\n\n"
                f"We are monitoring this line in real-time. Please stay in a safe spot, and we will update you by SMS every 10 minutes until the hazard is fully isolated."
            )
            policies = [
                "Municipal Emergency Electrical Protocol §4.2 (Immediate 30ft Perimeter)",
                "Rapid Hazard Dispatch SLA (Sub-30-Minute Guaranteed On-Site Assessment)",
                "Public Safety Directive 2026-B (Direct Supervisor Radio Escalation)"
            ]
            actions = [
                "Verify live GPS tracker of deployed Emergency Unit #9",
                "Trigger automated SMS perimeter warning to residents within 200m",
                "Keep emergency dispatch line open"
            ]

        elif emotion == "Angry":
            draft = (
                f"Dear {user_name},\n\n"
                f"You are completely right to feel angry about this. Having to deal with this disruption is unacceptable, "
                f"and we sincerely apologize for the frustration and delay you experienced.\n\n"
                f"I am personally taking ownership of Ticket #{tracking_num}. We have escalated this directly to our Senior Operations Manager. "
                f"Here is what is happening right now:\n"
                f"1. A dedicated repair crew has been assigned and scheduled.\n"
                f"2. Our QA team is auditing why this issue was not flagged earlier.\n"
                f"3. We will follow up with you directly with photographic proof of resolution as soon as the site is cleared.\n\n"
                f"Thank you for holding us accountable. You should not have had to wait, and we are making it right immediately."
            )
            policies = [
                "Customer Service Guarantee §12 (First-Contact Ownership & Escalation)",
                "Service Level Integrity Guarantee (Root-Cause Transparency Mandate)"
            ]
            actions = [
                "Assign senior resolver AGENT-409 directly to ticket",
                "Waive service fee / issue credit memo if applicable",
                "Schedule priority QA inspection within 4 hours"
            ]

        elif emotion == "Frustrated":
            draft = (
                f"Hello {user_name},\n\n"
                f"Thank you for reaching out and alerting us to this. We understand how frustrating it is to have your daily routine interrupted by this issue.\n\n"
                f"We have ingested your report through our AI triage command center (Ticket #{tracking_num}). "
                f"Our field engineering team has already reviewed your report details and scheduled remediation.\n\n"
                f"You can follow live progress on your citizen tracking portal at any time. We will notify you the moment repairs are complete."
            )
            policies = [
                "Municipal Quality Charter (Standard Remediation & Verification SLA)",
                "Open Status Feed Policy (Public Transparent Tracking)"
            ]
            actions = [
                "Confirm work order generation with municipal dispatch",
                "Link status updates to citizen's WhatsApp/SMS channel"
            ]

        else: # Calm / Standard
            draft = (
                f"Hello {user_name},\n\n"
                f"Thank you for contacting ComplainAI. We have registered your grievance under tracking ID #{tracking_num}.\n\n"
                f"Our systems have classified this under '{category}' with high priority. "
                f"Our automated workflows and field teams are actively working toward resolution. We will notify you once completed."
            )
            policies = [
                "Standard Operating Procedure §1.1 (Intake & Notification)"
            ]
            actions = [
                "Track ticket progression through standard workflow"
            ]

        return CopilotDraftResponse(
            complaint_id=complaint["id"],
            user_emotion=emotion,
            draft_message=draft,
            policy_citations=policies,
            recommended_actions=actions
        )

empathy_copilot = EmpathyCopilot()
