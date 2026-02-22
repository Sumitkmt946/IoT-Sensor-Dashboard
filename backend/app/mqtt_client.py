"""
MQTT client – subscribes to sensor topics, validates thresholds, persists data.
Runs on a background thread managed by FastAPI lifespan events.
"""

import json
import logging
from datetime import datetime
from threading import Thread

import paho.mqtt.client as mqtt

from app.config import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_TOPICS,
    THRESHOLDS,
    SENSOR_PARAMS,
)
from app.database import SessionLocal
from app.models import SensorData, Alert

logger = logging.getLogger("mqtt_client")
logger.setLevel(logging.INFO)


def _check_thresholds(payload: dict) -> tuple[list[str], dict, dict]:
    """
    Validate sensor values against configured thresholds.
    Returns (violated_keys, actual_values, threshold_values).
    """
    violated = []
    actual = {}
    threshold_info = {}

    for key in SENSOR_PARAMS:
        value = payload.get(key)
        if value is None:
            continue
        limits = THRESHOLDS[key]
        if value < limits["min"] or value > limits["max"]:
            violated.append(key)
            actual[key] = value
            threshold_info[key] = limits

    return violated, actual, threshold_info


def _compute_severity(violated_keys: list[str], payload: dict) -> str:
    """Return 'critical' if any value is > 20% outside the range, else 'warning'."""
    for key in violated_keys:
        value = payload[key]
        limits = THRESHOLDS[key]
        span = limits["max"] - limits["min"]
        if value < limits["min"] - 0.2 * span or value > limits["max"] + 0.2 * span:
            return "critical"
    return "warning"


def _on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("✅ Connected to MQTT broker")
        for topic in MQTT_TOPICS:
            client.subscribe(topic)
            logger.info(f"  📡 Subscribed to {topic}")
    else:
        logger.error(f"❌ MQTT connection failed with code {rc}")


def _on_message(client, userdata, msg):
    """Handle incoming MQTT messages."""
    try:
        payload = json.loads(msg.payload.decode())
        topic = msg.topic
        logger.info(f"📩 [{topic}] {payload}")

        db = SessionLocal()
        try:
            # ── Store raw sensor data ───────────────────────────────────
            sensor_data = SensorData(
                topic=topic,
                temperature=payload.get("temperature", 0),
                humidity=payload.get("humidity", 0),
                voltage=payload.get("voltage", 0),
                current=payload.get("current", 0),
                pressure=payload.get("pressure", 0),
                timestamp=datetime.utcnow(),
            )
            db.add(sensor_data)
            db.commit()
            db.refresh(sensor_data)

            # ── Check thresholds ────────────────────────────────────────
            violated, actual_vals, thresh_vals = _check_thresholds(payload)
            if violated:
                severity = _compute_severity(violated, payload)
                alert = Alert(
                    sensor_data_id=sensor_data.id,
                    topic=topic,
                    violated_keys=violated,
                    actual_values=actual_vals,
                    threshold_values=thresh_vals,
                    severity=severity,
                    timestamp=datetime.utcnow(),
                )
                db.add(alert)
                db.commit()
                logger.warning(
                    f"🚨 ALERT [{severity.upper()}] on {topic}: "
                    f"{violated} → {actual_vals}"
                )
        finally:
            db.close()

    except json.JSONDecodeError:
        logger.error(f"Invalid JSON on {msg.topic}: {msg.payload}")
    except Exception as e:
        logger.exception(f"Error processing message: {e}")


# ── Public interface ────────────────────────────────────────────────────────

_client: mqtt.Client | None = None
_thread: Thread | None = None


def start_mqtt():
    """Start the MQTT subscriber in a daemon thread."""
    global _client, _thread

    _client = mqtt.Client(client_id="fastapi-sensor-backend")
    _client.on_connect = _on_connect
    _client.on_message = _on_message

    try:
        _client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
    except Exception as e:
        logger.error(f"Could not connect to MQTT broker: {e}")
        logger.info("Backend will run without MQTT – use the API normally.")
        return

    _thread = Thread(target=_client.loop_forever, daemon=True)
    _thread.start()
    logger.info("🚀 MQTT background thread started")


def stop_mqtt():
    """Gracefully disconnect."""
    global _client
    if _client:
        _client.disconnect()
        logger.info("MQTT client disconnected")
