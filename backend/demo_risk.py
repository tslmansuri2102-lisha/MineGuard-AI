"""
MineGuard AI — End-to-End Pipeline & AI Risk Assessment Demonstration
Demonstrates real-time scenario transitions:
NORMAL -> HEAVY_RAIN -> PROGRESSIVE_INSTABILITY -> CRITICAL_COMBINED (Alert) -> RECOVERY.
"""

import os
import sys
import time

# Ensure repository root is on sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from ai.risk_engine import risk_engine
from backend.alerts import alert_service
from backend.services import simulation_service


def print_banner():
    print("=" * 70)
    print("      🛡️  MINEGUARD AI — ROCKFALL PREDICTION & EARLY WARNING SYSTEM")
    print("      Physics Sensor Simulation  →  AI Risk Engine  →  Live Alerting")
    print("=" * 70)
    print()


def display_step(scenario: str, step: int, reading: dict, prediction: dict):
    sensors = reading["sensors"]
    risk_level = prediction["risk_level"]
    risk_score = prediction["risk_score"]
    status = prediction["status"]
    action = prediction["recommended_action"]
    factors = prediction.get("factors", [])

    # Color/symbol badges
    badge_map = {
        "LOW": "🟢 LOW",
        "MODERATE": "🟡 MODERATE",
        "HIGH": "🟠 HIGH",
        "CRITICAL": "🔴 CRITICAL",
    }
    badge = badge_map.get(risk_level, risk_level)

    factor_str = ", ".join([f"{f['feature']} ({f['impact']})" for f in factors[:2]])

    print(f"[{scenario}] Step {step} | {reading['timestamp']}")
    print(f"  Telemetry: Disp={sensors['displacement_mm']:.1f}mm | Pore={sensors['pore_pressure_kpa']:.1f}kPa | Rain={sensors['rainfall_mm']:.1f}mm | Vib={sensors['vibration_g']:.2f}g | Strain={sensors['strain']:.2f}")
    print(f"  AI Assessment: {badge} (Score: {risk_score:.1f}/100) | Confidence: {prediction['confidence']:.2f} | Status: {status}")
    print(f"  Key Factors:   {factor_str}")
    print(f"  Recommended:   \"{action}\"")
    print("-" * 70)


def run_demo(steps_per_phase: int = 3, delay: float = 0.4):
    print_banner()

    scenarios = [
        ("1. NORMAL (Baseline Operations)", "NORMAL", "Baseline creep, safe operations"),
        ("2. HEAVY_RAIN (Storm Infiltration)", "HEAVY_RAIN", "Rainfall accumulation & rising pore pressure"),
        ("3. PROGRESSIVE_INSTABILITY (Slope Creep)", "PROGRESSIVE_INSTABILITY", "Accelerating shear strain & displacement creep"),
        ("4. CRITICAL_COMBINED (Catastrophic Risk)", "CRITICAL_COMBINED", "Multi-hazard convergence & automated alert triggering"),
        ("5. RECOVERY (Mitigation & Equilibrium)", "RECOVERY", "Bench stabilization & smooth return toward safe baseline"),
    ]

    for title, sc_enum, desc in scenarios:
        print(f"\n▶ TRANSITIONING SCENARIO: {title}")
        print(f"  Description: {desc}\n")
        simulation_service.start_simulation(scenario=sc_enum, interval=1.0, seed=42)

        for step in range(1, steps_per_phase + 1):
            reading = simulation_service.generate_next_reading()
            prediction = simulation_service.get_latest_prediction()
            display_step(sc_enum, step, reading, prediction)
            time.sleep(delay)

    # Show Alert Summary
    print("\n" + "=" * 70)
    print("📋 ALERT LOG SUMMARY (Simulated Dispatch Store)")
    print("=" * 70)
    alerts = alert_service.get_history(limit=5)
    if alerts:
        for idx, alt in enumerate(alerts, 1):
            print(f"  {idx}. [{alt['alert_id']}] Level: {alt['risk_level']} | Score: {alt['risk_score']:.1f} | Zone: {alt['zone_id']}")
            print(f"     Msg: {alt['message']}")
            print(f"     Action: {alt['recommended_action']}\n")
    else:
        print("  No critical alerts recorded.")

    print("=" * 70)
    print("✅ MineGuard AI End-to-End Pipeline Demonstration Completed Successfully.")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
