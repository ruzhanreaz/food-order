from fastapi import APIRouter, HTTPException
from app.schemas import Restaurant
from app.store import RESTAURANTS

router = APIRouter()

@router.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "restaurant"}

@router.get("/restaurants", response_model=list[Restaurant])
async def list_restaurants():
    return list(RESTAURANTS.values())

@router.get("/restaurants/{restaurant_id}", response_model=Restaurant)
async def get_restaurant(restaurant_id: str):
    restaurant = RESTAURANTS.get(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_id}' not found")
    return restaurant