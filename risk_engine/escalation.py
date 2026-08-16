"""
MineGuard AI — Risk Escalation & Trend Evaluator Module
"""

from typing import List


class EscalationEvaluator:
    """
    Evaluates risk trends, multi-sensor confirmation, and stale device confidence adjustments.
    """
    @staticmethod
    def calculate_trend(previous_scores: List[float]) -> str:
        """
        Calculate trend from historical risk score window.
        """
        if len(previous_scores) < 2:
            return "STABLE"
            
        recent_delta = previous_scores[-1] - previous_scores[-2]
        
        if recent_delta > 15.0:
            return "RAPIDLY_INCREASING"
        elif recent_delta > 3.0:
            return "INCREASING"
        elif recent_delta < -5.0:
            return "DECREASING"
        return "STABLE"

    @staticmethod
    def calculate_confidence(
        is_stale: bool,
        sensor_count_in_zone: int,
        is_isolated_anomaly: bool
    ) -> float:
        """
        Compute confidence rating (0.0 to 1.0).
        """
        base_confidence = 0.85
        
        # Stale data reduces confidence
        if is_stale:
            base_confidence -= 0.35
            
        # Multiple sensors agreeing increases confidence
        if sensor_count_in_zone >= 2:
            base_confidence += 0.10
            
        # Isolated single-sensor anomaly reduces confidence
        if is_isolated_anomaly and sensor_count_in_zone < 2:
            base_confidence -= 0.20
            
        return float(round(max(0.1, min(1.0, base_confidence)), 2))
