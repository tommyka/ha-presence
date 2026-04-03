from __future__ import annotations

from dataclasses import dataclass
import json
import logging
import threading
from typing import Any

from ha_presence.config import ServiceConfig

logger = logging.getLogger(__name__)

_CONNECT_TIMEOUT = 10  # seconds


@dataclass
class MqttTopics:
    availability: str
    status: str
    attributes: str
    discovery: str


def build_topics(config: ServiceConfig) -> MqttTopics:
    base = config.base_topic
    return MqttTopics(
        availability=f"{base}/availability",
        status=f"{base}/status",
        attributes=f"{base}/attributes",
        discovery=f"homeassistant/sensor/{config.hostname}_presence/config",
    )


class MqttPublisher:
    def __init__(self, config: ServiceConfig) -> None:
        self._config = config
        self._topics = build_topics(config)
        self._client: Any | None = None

    @property
    def topics(self) -> MqttTopics:
        return self._topics

    def connect(self) -> None:
        try:
            import paho.mqtt.client as mqtt  # type: ignore[import-untyped]
        except ModuleNotFoundError as exc:
            msg = "paho-mqtt is required. Install dependencies before running the service."
            raise RuntimeError(msg) from exc

        connected = threading.Event()
        connect_error: list[str] = []

        def on_connect(client: Any, userdata: Any, flags: Any, reason_code: Any, properties: Any) -> None:
            if reason_code.is_failure:
                connect_error.append(str(reason_code))
            else:
                connected.set()

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = on_connect
        if self._config.mqtt_username:
            client.username_pw_set(self._config.mqtt_username, self._config.mqtt_password)

        client.will_set(self._topics.availability, payload="offline", retain=True)
        client.connect(self._config.mqtt_host, self._config.mqtt_port)
        client.loop_start()

        if not connected.wait(timeout=_CONNECT_TIMEOUT):
            client.loop_stop()
            reason = connect_error[0] if connect_error else "timed out"
            msg = f"Failed to connect to MQTT broker at {self._config.mqtt_host}:{self._config.mqtt_port}: {reason}"
            raise RuntimeError(msg)

        client.publish(self._topics.availability, payload="online", qos=1, retain=True)
        self._client = client
        logger.info("Connected to MQTT broker at %s:%s", self._config.mqtt_host, self._config.mqtt_port)

    def publish_attributes(self, payload: dict[str, object]) -> None:
        self._publish_json(self._topics.attributes, payload, retain=False)

    def publish_status(self, payload: dict[str, object]) -> None:
        self._publish_json(self._topics.status, payload, retain=False)

    def publish_discovery(self) -> None:
        discovery = {
            "name": f"{self._config.hostname} Presence",
            "state_topic": self._topics.status,
            "availability_topic": self._topics.availability,
            "json_attributes_topic": self._topics.attributes,
            "unique_id": f"{self._config.hostname}_presence",
            "value_template": "{{ value_json.state }}",
            "device": {
                "identifiers": [self._config.hostname],
                "name": self._config.hostname,
                "manufacturer": "ha-presence",
                "model": "python-service",
            },
        }
        self._publish_json(self._topics.discovery, discovery, retain=True)

    def close(self) -> None:
        if self._client is None:
            return
        self._client.publish(self._topics.availability, payload="offline", qos=1, retain=True)
        self._client.loop_stop()
        self._client.disconnect()
        self._client = None

    def _publish_json(self, topic: str, payload: dict[str, object], retain: bool) -> None:
        if self._client is None:
            msg = "MQTT client is not connected"
            raise RuntimeError(msg)
        self._client.publish(topic, payload=json.dumps(payload), qos=1, retain=retain)

    def publish_attributes(self, payload: dict[str, object]) -> None:
        self._publish_json(self._topics.attributes, payload, retain=False)

    def publish_status(self, payload: dict[str, object]) -> None:
        self._publish_json(self._topics.status, payload, retain=False)

    def publish_discovery(self) -> None:
        discovery = {
            "name": f"{self._config.hostname} Presence",
            "state_topic": self._topics.status,
            "availability_topic": self._topics.availability,
            "json_attributes_topic": self._topics.attributes,
            "unique_id": f"{self._config.hostname}_presence",
            "value_template": "{{ value_json.state }}",
            "device": {
                "identifiers": [self._config.hostname],
                "name": self._config.hostname,
                "manufacturer": "ha-presence",
                "model": "python-service",
            },
        }
        self._publish_json(self._topics.discovery, discovery, retain=True)

    def close(self) -> None:
        if self._client is None:
            return
        self._client.publish(self._topics.availability, payload="offline", qos=1, retain=True)
        self._client.loop_stop()
        self._client.disconnect()
        self._client = None

    def _publish_json(self, topic: str, payload: dict[str, object], retain: bool) -> None:
        if self._client is None:
            msg = "MQTT client is not connected"
            raise RuntimeError(msg)
        self._client.publish(topic, payload=json.dumps(payload), qos=1, retain=retain)
