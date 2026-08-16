"""
MineGuard AI — MQTT Subscriber Interface for Physical ESP32 Sensors
"""

import json
from typing import Callable, Optional
from ml.utils import logger
from iot.sensor_schema import validate_raw_telemetry_dict


class MQTTClientHandler:
    """
    Simulated/Interface MQTT client subscriber handler for physical ESP32 hardware.
    """
    def __init__(self, broker_url: str = "localhost", port: int = 1883, topic: str = "mineguard/telemetry/#"):
        self.broker_url = broker_url
        self.port = port
        self.topic = topic
        self.on_message_callback: Optional[Callable] = None
        self.is_connected = False

    def connect(self):
        """Simulate/Connect to MQTT broker."""
        logger.info("Connecting MQTT Client to broker %s:%d (Topic: %s)...", self.broker_url, self.port, self.topic)
        self.is_connected = True

    def set_callback(self, callback: Callable):
        self.on_message_callback = callback

    def process_incoming_payload(self, raw_json_str: str):
        """Parse raw MQTT JSON string and route to callback."""
        try:
            payload = json.loads(raw_json_str)
            is_valid, schema_obj, err = validate_raw_telemetry_dict(payload)
            if not is_valid:
                logger.error("MQTT Received Malformed Telemetry: %s", err)
                return
            if self.on_message_callback:
                self.on_message_callback(schema_obj.to_dict())
        except Exception as e:
            logger.error("Failed to process MQTT message: %s", e)
