from datetime import datetime

from sqlalchemy import (
    Column, Integer, Float, String, DateTime, JSON, ForeignKey, Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class SensorData(Base):
    """Stores every raw MQTT message received."""

    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(String(255), nullable=False, index=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    voltage = Column(Float, nullable=False)
    current = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # One sensor reading can trigger one alert (optional)
    alert = relationship("Alert", back_populates="sensor_data", uselist=False)

    def __repr__(self):
        return f"<SensorData id={self.id} topic={self.topic}>"


class Alert(Base):
    """Stores threshold‑breach alerts."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_data_id = Column(
        Integer, ForeignKey("sensor_data.id"), nullable=False
    )
    topic = Column(String(255), nullable=False, index=True)
    violated_keys = Column(JSON, nullable=False)      # e.g. ["temperature", "voltage"]
    actual_values = Column(JSON, nullable=False)       # e.g. {"temperature": 75.2, ...}
    threshold_values = Column(JSON, nullable=False)    # e.g. {"temperature": {"min": -10, "max": 60}}
    severity = Column(String(20), nullable=False, default="warning")  # warning / critical
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    sensor_data = relationship("SensorData", back_populates="alert")

    def __repr__(self):
        return f"<Alert id={self.id} topic={self.topic} keys={self.violated_keys}>"
