"""
MineGuard AI — IoT Device & Sensor Manager Module
"""

from typing import Dict, List, Optional
from datetime import datetime, timezone
from ml.utils import logger


class DeviceManager:
    """
    Manages active IoT sensor registrations, zone mapping, and stale device detection.
    """
    def __init__(self, stale_threshold_seconds: float = 60.0):
        self.stale_threshold_seconds = stale_threshold_seconds
        self.devices: Dict[str, dict] = {}
        self.zones: Dict[str, dict] = {
            "ZONE-001": {"zone_id": "ZONE-001", "name": "North Bench Face", "latitude": 23.7954, "longitude": 86.4304},
            "ZONE-002": {"zone_id": "ZONE-002", "name": "East Wall Slope", "latitude": 23.7980, "longitude": 86.4340},
            "ZONE-003": {"zone_id": "ZONE-003", "name": "South Haul-Road Bench", "latitude": 23.7920, "longitude": 86.4280},
        }

    def register_telemetry(self, sensor_id: str, zone_id: str, lat: float, lon: float, timestamp_iso: str):
        """Update last seen timestamp and position for a sensor device."""
        now = datetime.now(timezone.utc)
        
        if zone_id not in self.zones:
            self.zones[zone_id] = {
                "zone_id": zone_id,
                "name": f"Mine Bench Zone ({zone_id})",
                "latitude": lat,
                "longitude": lon
            }
            
        self.devices[sensor_id] = {
            "sensor_id": sensor_id,
            "zone_id": zone_id,
            "latitude": lat,
            "longitude": lon,
            "last_seen_iso": timestamp_iso,
            "last_seen_time": now,
            "status": "ONLINE"
        }

    def check_device_status(self, sensor_id: str) -> str:
        """Check if a sensor is ONLINE or STALE."""
        if sensor_id not in self.devices:
            return "UNKNOWN"
            
        device = self.devices[sensor_id]
        last_seen = device["last_seen_time"]
        elapsed = (datetime.now(timezone.utc) - last_seen).total_seconds()
        
        if elapsed > self.stale_threshold_seconds:
            device["status"] = "STALE"
            return "STALE"
            
        device["status"] = "ONLINE"
        return "ONLINE"

    def get_zone_sensors(self, zone_id: str) -> List[dict]:
        """Get all sensors registered to a zone with their live status."""
        result = []
        for s_id, dev in self.devices.items():
            if dev["zone_id"] == zone_id:
                status = self.check_device_status(s_id)
                res = dev.copy()
                res["status"] = status
                result.append(res)
        return result

    def get_all_zones(self) -> List[dict]:
        return list(self.zones.values())

    def get_all_devices(self) -> List[dict]:
        for s_id in list(self.devices.keys()):
            self.check_device_status(s_id)
        return list(self.devices.values())
