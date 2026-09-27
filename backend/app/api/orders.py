import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order
from app.schemas import OrderCreate, OrderResponse
from app.redis_client import get_redis_client
from app.logger import logger

router = APIRouter(prefix="/orders", tags=["Orders"])
CACHE_TTL_SECONDS = 300


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_in: OrderCreate, db: Session = Depends(get_db)):
    """Creates a new order in PostgreSQL and invalidates/warms cache."""
    db_order = Order(
        customer_email=order_in.customer_email,
        item_name=order_in.item_name,
        quantity=order_in.quantity,
        total_amount=order_in.total_amount,
        status="CONFIRMED",
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Cache order in Redis
    redis_client = get_redis_client()
    if redis_client:
        try:
            cache_payload = {
                "id": db_order.id,
                "customer_email": db_order.customer_email,
                "item_name": db_order.item_name,
                "quantity": db_order.quantity,
                "total_amount": db_order.total_amount,
                "status": db_order.status,
                "created_at": db_order.created_at.isoformat(),
            }
            redis_client.setex(f"order:{db_order.id}", CACHE_TTL_SECONDS, json.dumps(cache_payload))
        except Exception as exc:
            logger.warning(f"Failed to cache order {db_order.id} in Redis: {exc}")

    logger.info(
        f"Order {db_order.id} created for {db_order.customer_email}",
        extra={"order_id": db_order.id, "customer": db_order.customer_email, "amount": db_order.total_amount}
    )
    return db_order


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Retrieves an order by ID using a cache-aside pattern (Redis -> PostgreSQL)."""
    redis_client = get_redis_client()
    if redis_client:
        try:
            cached_data = redis_client.get(f"order:{order_id}")
            if cached_data:
                logger.info(f"Cache HIT for order {order_id}", extra={"order_id": order_id, "cache": "hit"})
                order_dict = json.loads(cached_data)
                return OrderResponse(**order_dict)
        except Exception as exc:
            logger.warning(f"Redis get error for order {order_id}: {exc}")

    # Cache miss - query PostgreSQL
    logger.info(f"Cache MISS for order {order_id}", extra={"order_id": order_id, "cache": "miss"})
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        logger.warning(f"Order {order_id} not found", extra={"order_id": order_id, "status_code": 404})
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order {order_id} not found")

    # Warm cache
    if redis_client:
        try:
            cache_payload = {
                "id": order.id,
                "customer_email": order.customer_email,
                "item_name": order.item_name,
                "quantity": order.quantity,
                "total_amount": order.total_amount,
                "status": order.status,
                "created_at": order.created_at.isoformat(),
            }
            redis_client.setex(f"order:{order.id}", CACHE_TTL_SECONDS, json.dumps(cache_payload))
        except Exception as exc:
            logger.warning(f"Failed to warm cache for order {order.id}: {exc}")

    return order


@router.get("", response_model=List[OrderResponse])
def list_orders(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """Lists orders with pagination."""
    orders = db.query(Order).order_by(Order.id.desc()).offset(skip).limit(limit).all()
    return orders
