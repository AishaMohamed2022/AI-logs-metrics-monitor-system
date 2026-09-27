import time
from datetime import datetime, timezone
from fastapi import APIRouter, status, Response
from app.database import check_database_connection
from app.redis_client import check_redis_connection
from app.schemas import ReadinessResponse, LivenessResponse, ServiceStatus

router = APIRouter(prefix="/health", tags=["Health Checks"])
_START_TIME = time.time()


@router.get("/live", response_model=LivenessResponse, status_code=status.HTTP_200_OK)
def liveness_probe():
    """Kubernetes Liveness Probe: indicates whether the pod container process is alive."""
    uptime = time.time() - _START_TIME
    return LivenessResponse(
        status="UP",
        uptime_seconds=round(uptime, 2),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/ready", response_model=ReadinessResponse)
def readiness_probe(response: Response):
    """Kubernetes Readiness Probe: checks downstream dependencies (PostgreSQL & Redis)."""
    db_ok, db_msg = check_database_connection()
    redis_ok, redis_msg = check_redis_connection()

    all_ready = db_ok and redis_ok

    if not all_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(
        status="READY" if all_ready else "UNHEALTHY",
        database=ServiceStatus(status="UP" if db_ok else "DOWN", message=db_msg),
        redis=ServiceStatus(status="UP" if redis_ok else "DOWN", message=redis_msg),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
