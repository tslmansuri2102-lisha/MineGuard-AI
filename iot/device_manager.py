"""
MineGuard AI — IoT Device Manager

Manages mine monitoring sensors, their registration,
health status, and last-seen timestamps.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from iot.sensor_schema import SensorReading


@dataclass
class SensorDevice:
    """Metadata and health state for one physical sensor."""

    sensor_id: str
    mine_id: str
    zone_id: str
    sensor_type: str
    status: str = "offline"
    last_seen: Optional[str] = None

    def heartbeat(self, timestamp: Optional[str] = None) -> None:
        """Mark the sensor as online and update its last-seen time."""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()

        self.last_seen = timestamp
        self.status = "online"


class DeviceManager:
    """
    Registry and health manager for MineGuard IoT sensors.
    """

    def __init__(self, stale_after_seconds: int = 120):
        self.devices: Dict[str, SensorDevice] = {}
        self.stale_after_seconds = stale_after_seconds

    def register_device(
        self,
        sensor_id: str,
        mine_id: str,
        zone_id: str,
        sensor_type: str,
    ) -> SensorDevice:
        """Register a new sensor device."""

        if not sensor_id:
            raise ValueError("sensor_id cannot be empty")

        if not mine_id:
            raise ValueError("mine_id cannot be empty")

        if not zone_id:
            raise ValueError("zone_id cannot be empty")

        if not sensor_type:
            raise ValueError("sensor_type cannot be empty")

        if sensor_id in self.devices:
            raise ValueError(
                f"Sensor '{sensor_id}' is already registered"
            )

        device = SensorDevice(
            sensor_id=sensor_id,
            mine_id=mine_id,
            zone_id=zone_id,
            sensor_type=sensor_type,
        )

        self.devices[sensor_id] = device

        return device

    def heartbeat(
        self,
        sensor_id: str,
        timestamp: Optional[str] = None,
    ) -> SensorDevice:
        """Update the heartbeat of a registered sensor."""

        device = self.get_device(sensor_id)

        if device is None:
            raise KeyError(
                f"Unknown sensor: {sensor_id}"
            )

        device.heartbeat(timestamp)

        return device

    def process_reading(
        self,
        sensor_id: str,
        reading: SensorReading,
    ) -> SensorDevice:
        """
        Process a validated sensor reading and update
        the corresponding device heartbeat.
        """

        device = self.get_device(sensor_id)

        if device is None:
            raise KeyError(
                f"Unknown sensor: {sensor_id}"
            )

        if reading.mine_id != device.mine_id:
            raise ValueError(
                f"Reading mine_id '{reading.mine_id}' does not "
                f"match sensor mine '{device.mine_id}'"
            )

        if reading.zone_id != device.zone_id:
            raise ValueError(
                f"Reading zone_id '{reading.zone_id}' does not "
                f"match sensor zone '{device.zone_id}'"
            )

        device.heartbeat(reading.timestamp)

        return device

    def get_device(
        self,
        sensor_id: str,
    ) -> Optional[SensorDevice]:
        """Return a device by sensor ID."""
        return self.devices.get(sensor_id)

    def get_devices_by_zone(
        self,
        mine_id: str,
        zone_id: str,
    ) -> List[SensorDevice]:
        """Return all sensors assigned to a mine zone."""

        return [
            device
            for device in self.devices.values()
            if device.mine_id == mine_id
            and device.zone_id == zone_id
        ]

    def get_online_devices(self) -> List[SensorDevice]:
        """Return all currently online sensors."""
        self.refresh_status()

        return [
            device
            for device in self.devices.values()
            if device.status == "online"
        ]

    def refresh_status(
        self,
        now: Optional[datetime] = None,
    ) -> None:
        """
        Mark sensors as offline when their last heartbeat
        exceeds the configured stale threshold.
        """

        if now is None:
            now = datetime.now(timezone.utc)

        for device in self.devices.values():

            if not device.last_seen:
                device.status = "offline"
                continue

            try:
                last_seen = datetime.fromisoformat(
                    device.last_seen.replace("Z", "+00:00")
                )

                if last_seen.tzinfo is None:
                    last_seen = last_seen.replace(
                        tzinfo=timezone.utc
                    )

                age = (
                    now - last_seen
                ).total_seconds()

                device.status = (
                    "offline"
                    if age > self.stale_after_seconds
                    else "online"
                )

            except ValueError:
                device.status = "offline"

    def device_count(self) -> int:
        """Return total registered sensor count."""
        return len(self.devices)

    def online_count(self) -> int:
        """Return number of currently online sensors."""
        return len(self.get_online_devices())