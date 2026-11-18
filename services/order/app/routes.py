from datetime import datetime, timezone
import logging
import uuid
from fastapi import APIRouter, HTTPException, Request
from app.client import restaurant_client
from app.schemas import CreateOrderRequest, OrderResponse
from app.store import order_store

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "order"}

@router.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(payload: CreateOrderRequest, request: Request):
    correlation_id = request.state.correlation_id

    # 1. Fetch restaurant over HTTP and validate restaurant_id
    restaurant_data = await restaurant_client.fetch_restaurant(payload.restaurant_id, correlation_id)

    # 2. Validate every requested menu_item_id belongs to that restaurant
    valid_item_ids = {item["id"] for item in restaurant_data.get("menu", [])}
    for item in payload.items:
        if item.menu_item_id not in valid_item_ids:
            raise HTTPException(
                status_code=404,
                detail=f"Menu item '{item.menu_item_id}' not found in restaurant '{payload.restaurant_id}'",
            )

    # 3. Generate unique ID and persist safely
    order = OrderResponse(
        order_id=f"ord-{uuid.uuid4().hex[:12]}",
        correlation_id=correlation_id,
        restaurant_id=payload.restaurant_id,
        items=payload.items,
        status="CONFIRMED",
        created_at=datetime.now(timezone.utc),
    )
    await order_store.save(order)
    logger.info(f"correlation_id={correlation_id} created order_id={order.order_id}")
    return order

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str):
    order = await order_store.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")
    return order