import time
from typing import List, Dict, Any
from backend.models import ForecastingAlert

class FailureForecastingEngine:
    def __init__(self):
        self.alerts: List[ForecastingAlert] = [
            ForecastingAlert(
                id="ALERT-FC-901",
                headline="PREDICTIVE WARNING: 340% Surge in Voltage Fluctuations in Sector 4",
                category="Electrical Grid Infrastructure",
                location_zone="Sector 4 Substation / Oakridge School District",
                probability=0.92,
                historical_velocity_spike="+340% velocity (18 micro-burst reports over 3 hours vs baseline 1.1/day)",
                predicted_impact="High probability of catastrophic transformer blowout within 8-12 hours. Risk to 45,000 households and backup hospital feeder line.",
                recommended_action="Dispatch preventive load-balancing crew & infrared thermal scan to Substation 4B immediately before hardware failure.",
                severity="CRITICAL",
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                dispatched=False
            ),
            ForecastingAlert(
                id="ALERT-FC-902",
                headline="EARLY DETECTION: Water Pressure Drop Pattern along Grand Avenue Corridor",
                category="Hydro Utility & Water Mains",
                location_zone="Grand Ave (Between 5th and 12th St)",
                probability=0.78,
                historical_velocity_spike="+180% low-pressure complaints within 45 minutes",
                predicted_impact="Subterranean cavity formation and impending asphalt subsidence / sinkhole rupture.",
                recommended_action="Deploy acoustic leak detection sensors and throttle feeder valve V-12.",
                severity="HIGH",
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                dispatched=False
            )
        ]

    def get_active_alerts(self) -> List[ForecastingAlert]:
        return self.alerts

    def dispatch_preventative_crew(self, alert_id: str) -> Dict[str, Any]:
        for a in self.alerts:
            if a.id == alert_id:
                a.dispatched = True
                return {
                    "success": True,
                    "alert_id": alert_id,
                    "message": f"Preventative crew dispatched to {a.location_zone}. Crisis averted before failure occurred.",
                    "dispatched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
                }
        return {"success": False, "message": "Alert not found"}

failure_forecasting = FailureForecastingEngine()
