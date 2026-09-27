from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.database import Base


class Order(Base):
    """Business domain model: Orders."""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_email = Column(String(255), nullable=False, index=True)
    item_name = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(50), default="PENDING", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class IncidentLog(Base):
    """System incident tracking for AIOps RCA engine recording."""

    __tablename__ = "incident_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    severity = Column(String(20), nullable=False)
    metric_name = Column(String(100), nullable=False)
    anomaly_score = Column(Float, nullable=False)
    root_cause = Column(Text, nullable=True)
    recommended_action = Column(Text, nullable=True)
    status = Column(String(50), default="DETECTED", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
