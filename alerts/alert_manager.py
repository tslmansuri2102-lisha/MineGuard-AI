"""
MineGuard AI — Alert Escalation & Cooldown Manager
"""

from typing import Optional, Dict
from datetime import datetime, timezone
from alerts.alert_store import AlertStore
from ml.utils import logger


class AlertManager:
    """
    Evaluates risk engine outputs and manages alert creation, cooldown, deduplication, and escalation.
    """
    LEVEL_ORDER = {"INFO": 0, "WARNING": 1, "HIGH_RISK": 2, "CRITICAL": 3}
    RISK_LEVEL_TO_ALERT_LEVEL = {
        "LOW": "INFO",
        "MODERATE": "WARNING",
        "HIGH": "HIGH_RISK",
        "CRITICAL": "CRITICAL"
    }

    def __init__(self, alert_store: AlertStore = None, cooldown_seconds: float = 60.0):
        self.store = alert_store or AlertStore()
        self.cooldown_seconds = cooldown_seconds
        self.last_alert_by_zone: Dict[str, dict] = {}

    def evaluate_risk_and_trigger_alert(
        self,
        telemetry: dict,
        risk_result: dict
    ) -> Optional[dict]:
        """
        Evaluate risk result and trigger alert if thresholds exceeded and cooldown/deduplication rules met.
        
        Returns:
            dict or None: Created alert record if triggered, None if suppressed by cooldown.
        """
        zone_id = telemetry.get("zone_id", "ZONE-001")
        risk_level = risk_result.get("risk_level", "LOW")
        risk_score = risk_result.get("risk_score", 0.0)
        alert_level = self.RISK_LEVEL_TO_ALERT_LEVEL.get(risk_level, "INFO")
        
        # Suppress routine LOW / INFO alerts unless requested
        if alert_level == "INFO":
            return None
            
        now = datetime.now(timezone.utc)
        last_alert = self.last_alert_by_zone.get(zone_id)
        
        if last_alert:
            last_time = last_alert["timestamp_dt"]
            last_alert_level = last_alert["level"]
            elapsed = (now - last_time).total_seconds()
            
            # ESCALATION RULE: Bypass cooldown immediately if risk level escalates to higher severity
            is_escalation = self.LEVEL_ORDER.get(alert_level, 0) > self.LEVEL_ORDER.get(last_alert_level, 0)
            
            # COOLDOWN & DEDUPLICATION RULE: Suppress if within cooldown window and not escalating
            if elapsed < self.cooldown_seconds and not is_escalation:
                logger.debug("Alert for Zone %s suppressed by cooldown (%.1fs < %.1fs).",
                             zone_id, elapsed, self.cooldown_seconds)
                return None

        # Create new alert
        alert = self.store.create_alert(
            zone_id=zone_id,
            sensor_id=telemetry.get("sensor_id", "UNKNOWN"),
            risk_score=risk_score,
            risk_level=risk_level,
            triggering_factors=risk_result.get("contributing_factors", []),
            recommended_action=risk_result.get("recommended_action", ""),
            latitude=telemetry.get("latitude", 0.0),
            longitude=telemetry.get("longitude", 0.0),
            level=alert_level
        )
        
        self.last_alert_by_zone[zone_id] = {
            "timestamp_dt": now,
            "level": alert_level,
            "risk_score": risk_score
        }
        
        return alert
