import time
import math
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, HTTPException, status
from app.schemas import (
    CpuStressRequest,
    MemoryStressRequest,
    ErrorSpikeRequest,
    LatencyInjectionRequest,
)
from app.logger import logger

router = APIRouter(prefix="/chaos", tags=["Chaos Engineering"])

_memory_hog: list[bytes] = []


def _burn_cpu(duration_seconds: int):
    """Spikes CPU usage by running intense calculations in a busy loop."""
    end_time = time.time() + duration_seconds
    while time.time() < end_time:
        _ = [math.sqrt(x) for x in range(1000)]


@router.post("/cpu")
def trigger_cpu_stress(payload: CpuStressRequest):
    """Simulates a severe CPU spike using multi-threaded mathematical workloads."""
    logger.warning(
        f"CHAOS INJECTED: CPU stress initiated for {payload.duration_seconds}s across {payload.worker_threads} threads",
        extra={"chaos_type": "cpu_spike", "duration": payload.duration_seconds, "threads": payload.worker_threads}
    )

    with ThreadPoolExecutor(max_workers=payload.worker_threads) as executor:
        for _ in range(payload.worker_threads):
            executor.submit(_burn_cpu, payload.duration_seconds)

    return {
        "status": "COMPLETED",
        "message": f"Burned CPU across {payload.worker_threads} threads for {payload.duration_seconds} seconds.",
    }


@router.post("/memory")
def trigger_memory_stress(payload: MemoryStressRequest):
    """Simulates a memory leak by holding a large byte buffer in memory."""
    global _memory_hog
    logger.warning(
        f"CHAOS INJECTED: Allocating {payload.alloc_megabytes} MB for {payload.hold_seconds}s",
        extra={"chaos_type": "memory_leak", "megabytes": payload.alloc_megabytes}
    )

    # Allocate byte chunks (1 MB each)
    chunk = b"x" * (1024 * 1024)
    _memory_hog = [chunk for _ in range(payload.alloc_megabytes)]

    def release_later(seconds: int):
        time.sleep(seconds)
        global _memory_hog
        _memory_hog = []
        logger.info("CHAOS RECOVERY: Memory hog cleared from heap.", extra={"chaos_type": "memory_leak_resolved"})

    thread = threading.Thread(target=release_later, args=(payload.hold_seconds,), daemon=True)
    thread.start()

    return {
        "status": "ALLOCATED",
        "allocated_mb": payload.alloc_megabytes,
        "hold_seconds": payload.hold_seconds,
        "message": f"Allocated {payload.alloc_megabytes} MB. Memory will be released in {payload.hold_seconds} seconds.",
    }


@router.post("/error-rate")
def trigger_error_rate(payload: ErrorSpikeRequest):
    """Randomly injects HTTP 500 errors according to the specified error rate."""
    roll = random.random()
    if roll < payload.error_rate:
        logger.error(
            f"CHAOS INJECTED: Simulated internal server failure! (roll={roll:.2f} < rate={payload.error_rate})",
            extra={"chaos_type": "http_500_spike", "error_code": "CHAOS_500"}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chaos Simulation: Simulated downstream dependency failure.",
        )

    return {
        "status": "SUCCESS",
        "message": f"Request survived error threshold check (roll={roll:.2f} >= rate={payload.error_rate})",
    }


@router.post("/latency")
def trigger_latency(payload: LatencyInjectionRequest):
    """Injects artificial latency to trigger P99 response time degradation alerts."""
    sleep_time = payload.delay_milliseconds / 1000.0
    logger.warning(
        f"CHAOS INJECTED: Artificial latency delay of {payload.delay_milliseconds}ms",
        extra={"chaos_type": "latency_spike", "delay_ms": payload.delay_milliseconds}
    )
    time.sleep(sleep_time)
    return {
        "status": "COMPLETED",
        "injected_delay_ms": payload.delay_milliseconds,
    }
