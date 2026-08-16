"""
MineGuard AI — Local Alert Persistence Store
"""

import uuid
from typing import Dict, List, Optional
from datetime import datetime, timezone
from ml.utils import logger, save_json


class AlertStore:
    """
    In-memory / JSON persistence store for MineGuard AI safety alerts.
    """
    def __init__(self, filepath: str = None):
        self.filepath = filepath
        self.alerts: Dict[str, dict] = {}

    def create_alert(
        self,
        zone_id: str,
        sensor_id: str,
        risk_score: float,
        risk_level: str,
        triggering_factors: list,
        recommended_action: str,
        latitude: float,
        longitude: float,
        level: str = "WARNING"
    ) -> dict:
        """Create and store a new safety alert."""
        alert_id = f"ALERT-{uuid.uuid4().hex[:6].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        
        alert_record = {
            "alert_id": alert_id,
            "timestamp": now_iso,
            "zone_id": zone_id,
            "sensor_id": sensor_id,
            "level": level,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "triggering_factors": triggering_factors,
            "recommended_action": recommended_action,
            "latitude": latitude,
            "longitude": longitude,
            "status": "UNACKNOWLEDGED",
            "acknowledged_at": None,
            "resolved_at": None
        }
        
        self.alerts[alert_id] = alert_record
        logger.info("Created Alert [%s] Level: %s for Zone %s (Score: %.1f)",
                    alert_id, level, zone_id, risk_score)
        return alert_record

    def get_alert(self, alert_id: str) -> Optional[dict]:
        return self.alerts.get(alert_id)

    def get_all_alerts(self, zone_id: str = None) -> List[dict]:
        alerts_list = list(self.alerts.values())
        if zone_id:
            alerts_list = [a for a in alerts_list if a["zone_id"] == zone_id]
        return sorted(alerts_list, key=lambda x: x["timestamp"], reverse=True)

    def get_active_alerts(self) -> List[dict]:
        """Get unacknowledged or un-resolved active alerts."""
        return [a for a in self.alerts.values() if a["status"] != "RESOLVED"]

    def acknowledge_alert(self, alert_id: str) -> Optional[dict]:
        if alert_id not in self.alerts:
            return None
        alert = self.alerts[alert_id]
        alert["status"] = "ACKNOWLEDGED"
        alert["acknowledged_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        logger.info("Alert [%s] ACKNOWLEDGED.", alert_id)
        return alert

    def resolve_alert(self, alert_id: str) -> Optional[dict]:
        if alert_id not in self.alerts:
            return None
        alert = self.alerts[alert_id]
        alert["status"] = "RESOLVED"
        alert["resolved_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        logger.info("Alert [%s] RESOLVED.", alert_id)
        return alert
