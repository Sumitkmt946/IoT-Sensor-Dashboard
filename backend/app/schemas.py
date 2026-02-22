from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel


# ── Sensor Data Schemas ─────────────────────────────────────────────────────

class SensorDataBase(BaseModel):
    topic: str
    temperature: float
    humidity: float
    voltage: float
    current: float
    pressure: float


class SensorDataCreate(SensorDataBase):
    pass


class SensorDataResponse(SensorDataBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class SensorDataPaginated(BaseModel):
    items: List[SensorDataResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SensorStats(BaseModel):
    total_messages: int
    total_topics: int
    topic_counts: Dict[str, int]
    latest_timestamp: Optional[datetime] = None


# ── Alert Schemas ───────────────────────────────────────────────────────────

class AlertBase(BaseModel):
    topic: str
    violated_keys: List[str]
    actual_values: Dict[str, Any]
    threshold_values: Dict[str, Any]
    severity: str


class AlertResponse(AlertBase):
    id: int
    sensor_data_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class AlertPaginated(BaseModel):
    items: List[AlertResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AlertCountResponse(BaseModel):
    total_alerts: int
    critical_count: int
    warning_count: int


# ── Threshold Schema (for documentation) ───────────────────────────────────

class ThresholdRange(BaseModel):
    min: float
    max: float


class ThresholdsResponse(BaseModel):
    thresholds: Dict[str, ThresholdRange]
