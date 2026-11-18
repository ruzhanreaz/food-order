import logging
import httpx
from fastapi import HTTPException
from app.config import RESTAURANT_URL, HTTP_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)

class RestaurantClient:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=RESTAURANT_URL,
            timeout=httpx.Timeout(HTTP_TIMEOUT_SECONDS),
        )

    async def close(self):
        await self.client.aclose()

    async def fetch_restaurant(self, restaurant_id: str, correlation_id: str) -> dict:
        headers = {"X-Correlation-ID": correlation_id}
        try:
            response = await self.client.get(f"/restaurants/{restaurant_id}", headers=headers)
        except httpx.TimeoutException:
            logger.error(f"correlation_id={correlation_id} Restaurant service timed out")
            raise HTTPException(status_code=503, detail="Restaurant service timed out")
        except httpx.RequestError as exc:
            logger.error(f"correlation_id={correlation_id} Restaurant service unreachable: {exc}")
            raise HTTPException(status_code=503, detail="Restaurant service unavailable")

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_id}' not found")
        if response.status_code >= 500:
            raise HTTPException(status_code=503, detail="Restaurant service returned upstream error")

        response.raise_for_status()
        return response.json()

restaurant_client = RestaurantClient()