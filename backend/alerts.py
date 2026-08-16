"""
MineGuard AI — Alert Notification & Event Management System
Dispatches multi-channel alerts upon detection of HIGH or CRITICAL geotechnical risks.
Supports subscriber architecture for future SMS, Email, Push, and WhatsApp handlers.
"""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("mineguard.alerts")


@dataclass
class AlertEvent:
    """Represents a generated geotechnical safety alert event."""
    alert_id: str
    timestamp: str
    mine_id: str
    zone_id: str
    sensor_id: str
    risk_level: str
    risk_score: float
    message: str
    recommended_action: str
    factors: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "timestamp": self.timestamp,
            "mine_id": self.mine_id,
            "zone_id": self.zone_id,
            "sensor_id": self.sensor_id,
            "risk_level": self.risk_level,
            "risk_score": self.risk_score,
            "message": self.message,
            "recommended_action": self.recommended_action,
            "factors": self.factors,
        }


class AlertService:
    """
    Manages alert triggering, historical logging, and multi-channel dispatching.
    """

    def __init__(self, max_history: int = 200):
        self.max_history = max_history
        self._history: deque[AlertEvent] = deque(maxlen=max_history)
        self._subscribers: List[Callable[[AlertEvent], None]] = []
        self._alert_counter = 0

        # Register default logging subscriber
        self.register_subscriber(self._default_log_handler)

    def register_subscriber(self, subscriber: Callable[[AlertEvent], None]) -> None:
        """Registers a callback subscriber for alert dispatch (e.g. SMS, Email)."""
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)

    def _default_log_handler(self, alert: AlertEvent) -> None:
        """Default development handler logging formatted alert."""
        lines = [
            "",
            "🚨 " + "=" * 45,
            f"ALERT [{alert.alert_id}] — Risk: {alert.risk_level} (Score: {alert.risk_score:.1f})",
            f"Mine: {alert.mine_id} | Zone: {alert.zone_id} | Sensor: {alert.sensor_id}",
            f"Timestamp: {alert.timestamp}",
            f"Action: {alert.recommended_action}",
            "=" * 48,
        ]
        logger.warning("\n".join(lines))

    def evaluate_and_dispatch(self, prediction: Dict[str, Any]) -> Optional[AlertEvent]:
        """
        Evaluates a prediction dictionary. If risk_level is HIGH or CRITICAL,
        triggers and dispatches an AlertEvent to all registered subscribers.
        """
        risk_level = prediction.get("risk_level", "LOW")
        if risk_level not in ("HIGH", "CRITICAL"):
            return None

        self._alert_counter += 1
        alert_id = f"ALERT-{self._alert_counter:06d}"

        timestamp = prediction.get("timestamp", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        mine_id = prediction.get("mine_id", "MINE-001")
        zone_id = prediction.get("zone_id", "ZONE-003")
        sensor_id = prediction.get("sensor_id", "SENSOR-003")
        risk_score = float(prediction.get("risk_score", 0.0))
        recommended_action = prediction.get("recommended_action", "")
        factors = prediction.get("factors", [])

        message = (
            f"Geotechnical hazard detected in Zone {zone_id} of Mine {mine_id}. "
            f"Risk Level: {risk_level} (Score: {risk_score:.1f})."
        )

        alert = AlertEvent(
            alert_id=alert_id,
            timestamp=timestamp,
            mine_id=mine_id,
            zone_id=zone_id,
            sensor_id=sensor_id,
            risk_level=risk_level,
            risk_score=risk_score,
            message=message,
            recommended_action=recommended_action,
            factors=factors,
        )

        # Store in history buffer
        self._history.append(alert)

        # Dispatch to all subscribers
        for sub in self._subscribers:
            try:
                sub(alert)
            except Exception as e:
                logger.error(f"Error in alert subscriber {sub}: {e}")

        return alert

    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Returns recent alert history."""
        alerts = list(self._history)
        if limit is not None and limit > 0:
            alerts = alerts[-limit:]
        return [a.to_dict() for a in reversed(alerts)]

    def clear(self) -> None:
        """Clears alert history."""
        self._history.clear()


# Global default alert service instance
alert_service = AlertService()
