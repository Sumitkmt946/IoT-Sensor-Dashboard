"""API routes for sensor data retrieval."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import SensorData
from app.schemas import (
    SensorDataResponse,
    SensorDataPaginated,
    SensorStats,
    ThresholdsResponse,
)
from app.config import THRESHOLDS

router = APIRouter(prefix="/api/sensor-data", tags=["Sensor Data"])


@router.get("/", response_model=SensorDataPaginated)
def get_sensor_data(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    topic: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """Paginated raw sensor data with optional filters."""
    query = db.query(SensorData)

    if topic:
        query = query.filter(SensorData.topic == topic)
    if start_time:
        query = query.filter(SensorData.timestamp >= start_time)
    if end_time:
        query = query.filter(SensorData.timestamp <= end_time)

    total = query.count()
    items = (
        query.order_by(desc(SensorData.timestamp))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return SensorDataPaginated(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if total else 0,
    )


@router.get("/latest", response_model=list[SensorDataResponse])
def get_latest_readings(db: Session = Depends(get_db)):
    """Latest sensor reading for each topic."""
    subq = (
        db.query(
            SensorData.topic,
            func.max(SensorData.id).label("max_id"),
        )
        .group_by(SensorData.topic)
        .subquery()
    )
    results = (
        db.query(SensorData)
        .join(subq, SensorData.id == subq.c.max_id)
        .order_by(SensorData.topic)
        .all()
    )
    return results


@router.get("/stats", response_model=SensorStats)
def get_stats(db: Session = Depends(get_db)):
    """Aggregate statistics."""
    total = db.query(func.count(SensorData.id)).scalar() or 0
    topics = (
        db.query(SensorData.topic, func.count(SensorData.id))
        .group_by(SensorData.topic)
        .all()
    )
    latest = db.query(func.max(SensorData.timestamp)).scalar()

    return SensorStats(
        total_messages=total,
        total_topics=len(topics),
        topic_counts={t: c for t, c in topics},
        latest_timestamp=latest,
    )


@router.get("/thresholds", response_model=ThresholdsResponse)
def get_thresholds():
    """Return currently configured thresholds."""
    return ThresholdsResponse(thresholds=THRESHOLDS)


@router.get("/topics", response_model=list[str])
def get_topics(db: Session = Depends(get_db)):
    """List all topics that have sent data."""
    rows = db.query(SensorData.topic).distinct().all()
    return [r[0] for r in rows]
