from datetime import datetime
from pydantic import BaseModel, Field

class OrderItemRequest(BaseModel):
    menu_item_id: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0, description="Must be strictly greater than 0")

class CreateOrderRequest(BaseModel):
    restaurant_id: str = Field(..., min_length=1)
    items: list[OrderItemRequest] = Field(..., min_length=1)

class OrderResponse(BaseModel):
    order_id: str
    correlation_id: str
    restaurant_id: str
    items: list[OrderItemRequest]
    status: str
    created_at: datetime