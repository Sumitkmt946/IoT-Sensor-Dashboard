"""API routes for alerts."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Alert
from app.schemas import AlertResponse, AlertPaginated, AlertCountResponse

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("/", response_model=AlertPaginated)
def get_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    topic: Optional[str] = None,
    severity: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """Paginated alerts with optional filters."""
    query = db.query(Alert)

    if topic:
        query = query.filter(Alert.topic == topic)
    if severity:
        query = query.filter(Alert.severity == severity)
    if start_time:
        query = query.filter(Alert.timestamp >= start_time)
    if end_time:
        query = query.filter(Alert.timestamp <= end_time)

    total = query.count()
    items = (
        query.order_by(desc(Alert.timestamp))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return AlertPaginated(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size if total else 0,
    )


@router.get("/recent", response_model=list[AlertResponse])
def get_recent_alerts(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Most recent alerts."""
    return (
        db.query(Alert)
        .order_by(desc(Alert.timestamp))
        .limit(limit)
        .all()
    )


@router.get("/count", response_model=AlertCountResponse)
def get_alert_counts(db: Session = Depends(get_db)):
    """Alert count breakdown by severity."""
    total = db.query(func.count(Alert.id)).scalar() or 0
    critical = (
        db.query(func.count(Alert.id))
        .filter(Alert.severity == "critical")
        .scalar() or 0
    )
    warning = (
        db.query(func.count(Alert.id))
        .filter(Alert.severity == "warning")
        .scalar() or 0
    )
    return AlertCountResponse(
        total_alerts=total,
        critical_count=critical,
        warning_count=warning,
    )
