"""
MineGuard AI — Risk Explainability Engine
Identifies and ranks the primary contributing geotechnical factors for every risk assessment.
"""

from typing import Any, Dict, List


class ExplainabilityEngine:
    """
    Analyzes extracted sensor features and attributes relative risk contributions.
    Returns structured, human-interpretable factor rankings (HIGH, MEDIUM, LOW).
    """

    def explain(self, features: Dict[str, float], risk_score: float) -> List[Dict[str, str]]:
        """
        Determines the main contributing factors based on feature severity.

        Returns:
            List of dicts: [{"feature": "displacement_rate", "impact": "HIGH"}, ...]
        """
        disp = features.get("displacement_mm", 4.2)
        disp_rate = features.get("displacement_rate", 0.0)
        pore = features.get("pore_pressure_kpa", 31.5)
        pore_rate = features.get("pore_pressure_rate", 0.0)
        rain = features.get("rainfall_mm", 3.2)
        vib = features.get("vibration_g", 0.18)
        strain = features.get("strain", 0.21)

        candidate_factors = []

        # 1. Displacement velocity & magnitude
        if disp_rate > 2.0 or disp > 30.0:
            candidate_factors.append(("displacement_rate", "HIGH", disp_rate * 25.0 + disp))
        elif disp_rate > 0.5 or disp > 12.0:
            candidate_factors.append(("displacement_rate", "MEDIUM", disp_rate * 15.0 + disp))
        elif disp > 6.0:
            candidate_factors.append(("displacement_mm", "LOW", disp))

        # 2. Pore water pressure
        if pore > 60.0 or pore_rate > 1.5:
            candidate_factors.append(("pore_pressure_kpa", "HIGH", pore + pore_rate * 10))
        elif pore > 45.0 or pore_rate > 0.4:
            candidate_factors.append(("pore_pressure_kpa", "MEDIUM", pore))
        elif pore > 35.0:
            candidate_factors.append(("pore_pressure_kpa", "LOW", pore))

        # 3. Rainfall accumulation
        if rain > 45.0:
            candidate_factors.append(("rainfall_mm", "HIGH", rain))
        elif rain > 15.0:
            candidate_factors.append(("rainfall_mm", "MEDIUM", rain))
        elif rain > 5.0:
            candidate_factors.append(("rainfall_mm", "LOW", rain))

        # 4. Vibration amplitude
        if vib > 1.2:
            candidate_factors.append(("vibration_g", "HIGH", vib * 30))
        elif vib > 0.4:
            candidate_factors.append(("vibration_g", "MEDIUM", vib * 20))
        elif vib > 0.22:
            candidate_factors.append(("vibration_g", "LOW", vib * 10))

        # 5. Rock strain
        if strain > 0.6:
            candidate_factors.append(("strain", "HIGH", strain * 100))
        elif strain > 0.35:
            candidate_factors.append(("strain", "MEDIUM", strain * 50))

        # Sort candidate factors by impact weight descending
        impact_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        candidate_factors.sort(key=lambda x: (impact_order.get(x[1], 0), x[2]), reverse=True)

        # Format output
        results = []
        seen_features = set()
        for feat_name, impact_str, _ in candidate_factors:
            if feat_name not in seen_features:
                seen_features.add(feat_name)
                results.append({"feature": feat_name, "impact": impact_str})
                if len(results) >= 4:
                    break

        # If no significant factors were elevated (e.g. NORMAL conditions)
        if not results:
            results.append({"feature": "baseline_stability", "impact": "LOW"})

        return results
