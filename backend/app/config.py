import os
from dotenv import load_dotenv

load_dotenv()


# ── Database ────────────────────────────────────────────────────────────────
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "rootpassword")
DB_NAME = os.getenv("DB_NAME", "sensor_dashboard")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ── MQTT ────────────────────────────────────────────────────────────────────
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))

# Topics to subscribe
MQTT_TOPICS = [
    "sensor/plant1/boiler",
    "sensor/plant1/turbine",
    "sensor/plant2/compressor",
    "sensor/plant2/generator",
    "sensor/plant3/hvac",
    "sensor/plant3/motor",
    "sensor/warehouse/cold_storage",
    "sensor/warehouse/conveyor",
]

# ── Sensor Thresholds ──────────────────────────────────────────────────────
# Each key maps to {"min": <lower_bound>, "max": <upper_bound>}
THRESHOLDS = {
    "temperature": {"min": -10.0, "max": 60.0},    # °C
    "humidity":    {"min": 10.0,  "max": 90.0},     # %
    "voltage":    {"min": 180.0, "max": 260.0},     # V
    "current":    {"min": 0.0,   "max": 30.0},      # A
    "pressure":   {"min": 950.0, "max": 1050.0},    # hPa
}

SENSOR_PARAMS = list(THRESHOLDS.keys())
