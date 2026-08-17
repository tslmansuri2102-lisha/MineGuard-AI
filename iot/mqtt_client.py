"""
MineGuard AI — MQTT Sensor Client

Provides a lightweight MQTT-compatible telemetry interface.

The client supports:
1. Publishing sensor readings.
2. Receiving telemetry through callbacks.
3. Local/in-memory mode for simulation and testing.
4. Optional real MQTT support when paho-mqtt is installed.
"""

import json
from typing import Callable, Dict, List, Optional

from iot.sensor_schema import SensorReading


class MQTTClient:
    """
    MQTT telemetry client for MineGuard AI.

    By default, the client operates in local mode so the
    simulation can be tested without requiring an MQTT broker.
    """

    def __init__(
        self,
        broker_host: str = "localhost",
        broker_port: int = 1883,
        client_id: str = "mineguard-iot",
        use_real_mqtt: bool = False,
    ):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id
        self.use_real_mqtt = use_real_mqtt

        self.connected = False
        self.subscriptions: Dict[
            str, List[Callable[[SensorReading], None]]
        ] = {}

        self.published_messages: List[Dict] = []

        self._mqtt_client = None

    def connect(self) -> bool:
        """
        Connect to MQTT broker.

        In local mode, this simply activates the client.
        """

        if not self.use_real_mqtt:
            self.connected = True
            return True

        try:
            import paho.mqtt.client as mqtt
        except ImportError as exc:
            raise RuntimeError(
                "paho-mqtt is required for real MQTT mode. "
                "Install it with: pip install paho-mqtt"
            ) from exc

        self._mqtt_client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.client_id,
        )

        self._mqtt_client.connect(
            self.broker_host,
            self.broker_port,
            keepalive=60,
        )

        self._mqtt_client.loop_start()
        self.connected = True

        return True

    def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""

        if self._mqtt_client is not None:
            self._mqtt_client.loop_stop()
            self._mqtt_client.disconnect()

        self.connected = False

    def subscribe(
        self,
        topic: str,
        callback: Callable[[SensorReading], None],
    ) -> None:
        """
        Subscribe to a telemetry topic.

        The callback receives a validated SensorReading.
        """

        if not topic:
            raise ValueError("topic cannot be empty")

        if not callable(callback):
            raise ValueError("callback must be callable")

        self.subscriptions.setdefault(topic, []).append(callback)

        if self._mqtt_client is not None:
            self._mqtt_client.subscribe(topic)

    def publish(
        self,
        topic: str,
        reading: SensorReading,
    ) -> bool:
        """
        Publish a validated sensor reading.

        In local mode, the message is stored and immediately
        delivered to local subscribers.
        """

        if not self.connected:
            raise RuntimeError(
                "MQTT client is not connected"
            )

        if not isinstance(reading, SensorReading):
            raise TypeError(
                "reading must be a SensorReading instance"
            )

        payload = reading.to_dict()

        message = {
            "topic": topic,
            "payload": payload,
        }

        self.published_messages.append(message)

        if self._mqtt_client is not None:
            self._mqtt_client.publish(
                topic,
                json.dumps(payload),
            )

        self._deliver_local(topic, reading)

        return True

    def receive(
        self,
        topic: str,
        payload: Dict,
    ) -> SensorReading:
        """
        Validate and process an incoming telemetry message.

        Returns:
            SensorReading: validated sensor reading.
        """

        reading = SensorReading.from_dict(payload)

        self._deliver_local(topic, reading)

        return reading

    def _deliver_local(
        self,
        topic: str,
        reading: SensorReading,
    ) -> None:
        """Deliver a reading to local subscribers."""

        callbacks = self.subscriptions.get(topic, [])

        for callback in callbacks:
            callback(reading)

    def is_connected(self) -> bool:
        """Return current connection status."""
        return self.connected

    def published_count(self) -> int:
        """Return number of locally published messages."""
        return len(self.published_messages)