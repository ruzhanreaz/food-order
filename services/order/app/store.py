import asyncio
from app.schemas import OrderResponse

class OrderStore:
    def __init__(self):
        self._orders: dict[str, OrderResponse] = {}
        self._lock = asyncio.Lock()

    async def save(self, order: OrderResponse) -> OrderResponse:
        async with self._lock:
            if order.order_id in self._orders:
                raise ValueError("Duplicate order_id collision")
            self._orders[order.order_id] = order
            return order

    async def get(self, order_id: str) -> OrderResponse | None:
        async with self._lock:
            return self._orders.get(order_id)

order_store = OrderStore()