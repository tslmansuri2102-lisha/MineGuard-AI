"""
MineGuard AI — Deterministic Sensor Simulator CLI
"""

import time
import argparse
import requests
from ml.utils import logger
from simulation.scenarios import ScenarioGenerator
from simulation.telemetry import create_simulated_telemetry


def run_simulation(
    scenario: str = "NORMAL",
    zone_id: str = "ZONE-003",
    sensor_id: str = "SENSOR-003",
    interval: float = 1.0,
    duration: int = 10,
    seed: int = 42,
    api_url: str = None
) -> list:
    """
    Run deterministic telemetry simulation loop.
    
    Returns:
        list: List of generated TelemetrySchema dictionaries.
    """
    logger.info("Starting Simulator [Scenario: %s | Zone: %s | Sensor: %s | Seed: %d]",
                scenario, zone_id, sensor_id, seed)
                
    generator = ScenarioGenerator(scenario=scenario, seed=seed)
    total_steps = max(1, int(duration / interval))
    generated_events = []

    for step in range(total_steps):
        metrics = generator.generate_step(step_idx=step, total_steps=total_steps)
        telemetry_obj = create_simulated_telemetry(
            step_idx=step,
            scenario_metrics=metrics,
            zone_id=zone_id,
            sensor_id=sensor_id
        )
        payload = telemetry_obj.to_dict()
        generated_events.append(payload)
        
        logger.info("[Step %d/%d] Vib: %.2fg | Strain: %.2f | Disp: %.1fmm | Vel: %.3fmm/s | Rain: %.1fmm",
                    step + 1, total_steps, payload["vibration_g"], payload["strain"],
                    payload["displacement_mm"], payload["slope_velocity_mm_s"], payload["rainfall_mm"])
                    
        if api_url:
            try:
                res = requests.post(api_url, json=payload, timeout=3)
                logger.info(" Posted payload to %s -> Status: %d", api_url, res.status_code)
            except Exception as e:
                logger.warning(" Failed to POST telemetry to %s: %s", api_url, e)
                
        if interval > 0 and step < total_steps - 1:
            time.sleep(interval)
            
    logger.info("Simulation completed. Total events generated: %d", len(generated_events))
    return generated_events


def main():
    parser = argparse.ArgumentParser(description="MineGuard AI Sensor Telemetry Simulator")
    parser.add_argument("--scenario", type=str, default="NORMAL", choices=["NORMAL", "DEVELOPING_INSTABILITY", "HIGH_RISK", "CRITICAL_ROCKFALL"])
    parser.add_argument("--zone", type=str, default="ZONE-003", help="Zone ID")
    parser.add_argument("--sensor", type=str, default="SENSOR-003", help="Sensor ID")
    parser.add_argument("--interval", type=float, default=1.0, help="Interval between events in seconds")
    parser.add_argument("--duration", type=int, default=10, help="Total duration of simulation in seconds")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--api-url", type=str, default=None, help="HTTP API POST target endpoint")
    
    args = parser.parse_args()
    run_simulation(
        scenario=args.scenario,
        zone_id=args.zone,
        sensor_id=args.sensor,
        interval=args.interval,
        duration=args.duration,
        seed=args.seed,
        api_url=args.api_url
    )


if __name__ == "__main__":
    main()
