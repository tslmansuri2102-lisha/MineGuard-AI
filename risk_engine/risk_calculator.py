"""
MineGuard AI — Risk Fusion Calculator Module
"""

from typing import Dict, Any, List
from risk_engine.thresholds import DEFAULT_RISK_WEIGHTS, RISK_LEVEL_BOUNDS, RECOMMENDED_ACTIONS
from risk_engine.escalation import EscalationEvaluator
from ml.utils import logger


class RiskCalculator:
    """
    Fuses ML probability, geomechanical sensor trends, weather, and auxiliary human reports
    into a unified 0-100 Risk Score and Categorical Risk Level.
    """
    def __init__(self, weights: dict = None):
        self.weights = weights or DEFAULT_RISK_WEIGHTS
        self.history_by_zone: Dict[str, List[float]] = {}

    def calculate_risk(
        self,
        telemetry: dict,
        ml_result: dict,
        rolling_features: dict = None,
        is_stale: bool = False,
        sensor_count_in_zone: int = 1
    ) -> Dict[str, Any]:
        """
        Compute risk score, risk level, confidence, and contributing factors.
        """
        zone_id = telemetry.get("zone_id", "ZONE-001")
        rolling = rolling_features or {}
        
        # 1. Normalize Sub-scores (0 to 100)
        ml_prob = ml_result.get("ml_probability", 0.0)
        ml_score = ml_prob * 100.0
        
        vib = telemetry.get("vibration_g", 0.0)
        vib_score = min(100.0, (vib / 5.0) * 100.0)
        
        disp = telemetry.get("displacement_mm", 0.0)
        disp_score = min(100.0, (disp / 100.0) * 100.0)
        
        vel = telemetry.get("slope_velocity_mm_s", 0.0)
        vel_score = min(100.0, (vel / 2.0) * 100.0)
        
        strain = telemetry.get("strain", 0.0)
        strain_score = min(100.0, (strain / 5.0) * 100.0)
        
        anomaly = rolling.get("sensor_anomaly_score", 0.0)
        anomaly_score = min(100.0, anomaly * 100.0)
        
        rain = telemetry.get("rainfall_mm", 0.0)
        rain_score = min(100.0, (rain / 80.0) * 100.0)
        
        reports = telemetry.get("human_report_count", 0)
        report_score = min(100.0, reports * 25.0)
        
        # 2. Weighted Sum Fusion
        fused_score = (
            ml_score * self.weights["ml_probability"] +
            vib_score * self.weights["vibration_trend"] +
            disp_score * self.weights["displacement_trend"] +
            vel_score * self.weights["slope_velocity"] +
            strain_score * self.weights["strain_trend"] +
            anomaly_score * self.weights["sensor_anomaly"] +
            rain_score * self.weights["rainfall"] +
            report_score * self.weights["human_reports"]
        )
        
        final_risk_score = float(round(max(0.0, min(100.0, fused_score)), 1))
        
        # 3. Determine Risk Level
        risk_level = "LOW"
        for low, high, level in RISK_LEVEL_BOUNDS:
            if low <= final_risk_score <= high:
                risk_level = level
                break
                
        # Update zone history
        if zone_id not in self.history_by_zone:
            self.history_by_zone[zone_id] = []
        self.history_by_zone[zone_id].append(final_risk_score)
        if len(self.history_by_zone[zone_id]) > 20:
            self.history_by_zone[zone_id].pop(0)
            
        # 4. Trend & Confidence Calculation
        trend = EscalationEvaluator.calculate_trend(self.history_by_zone[zone_id])
        is_isolated_anomaly = (anomaly > 0.8 and sensor_count_in_zone < 2)
        confidence = EscalationEvaluator.calculate_confidence(
            is_stale=is_stale,
            sensor_count_in_zone=sensor_count_in_zone,
            is_isolated_anomaly=is_isolated_anomaly
        )
        
        # 5. Extract Contributing Factors
        factors = [
            {"feature": "ml_probability", "score": round(ml_score, 1), "weight": self.weights["ml_probability"], "description": f"ML model predicted failure probability ({ml_prob*100:.1f}%)"},
            {"feature": "vibration_g", "score": round(vib_score, 1), "weight": self.weights["vibration_trend"], "description": f"Ground vibration ({vib}g)"},
            {"feature": "displacement_mm", "score": round(disp_score, 1), "weight": self.weights["displacement_trend"], "description": f"Cumulative displacement ({disp}mm)"},
            {"feature": "slope_velocity_mm_s", "score": round(vel_score, 1), "weight": self.weights["slope_velocity"], "description": f"Slope movement velocity ({vel}mm/s)"},
            {"feature": "strain", "score": round(strain_score, 1), "weight": self.weights["strain_trend"], "description": f"Microstrain deformation ({strain})"}
        ]
        factors = sorted(factors, key=lambda x: x["score"] * x["weight"], reverse=True)
        
        return {
            "risk_score": final_risk_score,
            "risk_level": risk_level,
            "trend": trend,
            "confidence": confidence,
            "contributing_factors": factors[:4],
            "recommended_action": RECOMMENDED_ACTIONS.get(risk_level, RECOMMENDED_ACTIONS["LOW"])
        }
