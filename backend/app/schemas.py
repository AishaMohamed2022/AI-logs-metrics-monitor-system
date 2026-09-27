from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# Order Schemas
class OrderCreate(BaseModel):
    customer_email: EmailStr
    item_name: str = Field(..., min_length=1, max_length=255)
    quantity: int = Field(default=1, ge=1)
    total_amount: float = Field(..., gt=0.0)


class OrderResponse(BaseModel):
    id: int
    customer_email: str
    item_name: str
    quantity: int
    total_amount: float
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Health Schemas
class ServiceStatus(BaseModel):
    status: str
    message: Optional[str] = None


class ReadinessResponse(BaseModel):
    status: str
    database: ServiceStatus
    redis: ServiceStatus
    timestamp: str


class LivenessResponse(BaseModel):
    status: str
    uptime_seconds: float
    timestamp: str


# Chaos Simulation Schemas
class CpuStressRequest(BaseModel):
    duration_seconds: int = Field(default=5, ge=1, le=60)
    worker_threads: int = Field(default=2, ge=1, le=8)


class MemoryStressRequest(BaseModel):
    alloc_megabytes: int = Field(default=50, ge=10, le=500)
    hold_seconds: int = Field(default=5, ge=1, le=60)


class ErrorSpikeRequest(BaseModel):
    error_rate: float = Field(default=0.5, ge=0.0, le=1.0)
    duration_seconds: int = Field(default=10, ge=1, le=60)


class LatencyInjectionRequest(BaseModel):
    delay_milliseconds: int = Field(default=1000, ge=50, le=10000)
