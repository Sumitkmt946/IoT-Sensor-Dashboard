"""
MQTT Sensor Data Simulator
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Publishes random (but realistic) sensor readings to MQTT topics.
About 20% of the time it intentionally generates out‑of‑range values
so the backend alert system can be tested.

Usage:
    python -m simulator.mqtt_simulator          # from backend/
    python simulator/mqtt_simulator.py          # direct
"""

import json
import random
import time
import sys
import os

import paho.mqtt.client as mqtt

# Allow importing app.config when run from backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_TOPICS, THRESHOLDS

PUBLISH_INTERVAL = 3  # seconds between rounds


def _random_value(key: str, force_breach: bool = False) -> float:
    limits = THRESHOLDS[key]
    lo, hi = limits["min"], limits["max"]

    if force_breach:
        # Go 10‑40 % beyond the boundary
        if random.choice([True, False]):
            return round(hi + random.uniform(0.1, 0.4) * (hi - lo), 2)
        else:
            return round(lo - random.uniform(0.1, 0.4) * (hi - lo), 2)
    else:
        return round(random.uniform(lo, hi), 2)


def generate_payload(breach_probability: float = 0.20) -> dict:
    """Create a sensor-data payload; ~breach_probability chance per key of breaching."""
    payload = {}
    for key in THRESHOLDS:
        breach = random.random() < breach_probability
        payload[key] = _random_value(key, force_breach=breach)
    return payload


def main():
    client = mqtt.Client(client_id="sensor-simulator")

    print(f"🔌 Connecting to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT} …")
    try:
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
    except Exception as e:
        print(f"❌ Cannot connect to broker: {e}")
        sys.exit(1)

    client.loop_start()
    print("✅ Connected! Publishing sensor data …\n")

    try:
        while True:
            # Pick 3–5 random topics per round
            topics = random.sample(MQTT_TOPICS, k=min(random.randint(3, 5), len(MQTT_TOPICS)))
            for topic in topics:
                payload = generate_payload()
                msg = json.dumps(payload)
                client.publish(topic, msg)

                # Pretty print
                breaches = [
                    k for k in payload
                    if payload[k] < THRESHOLDS[k]["min"] or payload[k] > THRESHOLDS[k]["max"]
                ]
                flag = " 🚨" if breaches else ""
                print(f"  📤 {topic}  →  {msg}{flag}")

            print(f"  ── sleeping {PUBLISH_INTERVAL}s ──\n")
            time.sleep(PUBLISH_INTERVAL)

    except KeyboardInterrupt:
        print("\n🛑 Simulator stopped.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
