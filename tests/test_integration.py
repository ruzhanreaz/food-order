import asyncio
import httpx
import pytest

ORDER_URL = "http://localhost:8000"
RESTAURANT_URL = "http://localhost:8001"

@pytest.mark.asyncio
async def test_01_health_checks():
    async with httpx.AsyncClient() as client:
        r1 = await client.get(f"{RESTAURANT_URL}/healthz")
        r2 = await client.get(f"{ORDER_URL}/healthz")
        assert r1.status_code == 200
        assert r2.status_code == 200

@pytest.mark.asyncio
async def test_02_list_seeded_restaurants():
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{RESTAURANT_URL}/restaurants")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 3
        total_items = sum(len(r["menu"]) for r in data)
        assert total_items >= 6

@pytest.mark.asyncio
async def test_03_create_and_retrieve_order_success():
    payload = {
        "restaurant_id": "rest-1",
        "items": [{"menu_item_id": "item-101", "quantity": 2}],
    }
    headers = {"X-Correlation-ID": "test-trace-123"}
    async with httpx.AsyncClient() as client:
        create_res = await client.post(f"{ORDER_URL}/orders", json=payload, headers=headers)
        assert create_res.status_code == 201
        assert create_res.headers.get("X-Correlation-ID") == "test-trace-123"
        body = create_res.json()
        assert body["status"] == "CONFIRMED"
        assert "order_id" in body and "created_at" in body

        get_res = await client.get(f"{ORDER_URL}/orders/{body['order_id']}")
        assert get_res.status_code == 200
        assert get_res.json()["order_id"] == body["order_id"]

@pytest.mark.asyncio
async def test_04_reject_bad_quantities_and_missing_fields():
    async with httpx.AsyncClient() as client:
        # Zero quantity -> 400
        r1 = await client.post(f"{ORDER_URL}/orders", json={
            "restaurant_id": "rest-1",
            "items": [{"menu_item_id": "item-101", "quantity": 0}],
        })
        assert r1.status_code == 400

        # Missing items field -> 400
        r2 = await client.post(f"{ORDER_URL}/orders", json={"restaurant_id": "rest-1"})
        assert r2.status_code == 400

@pytest.mark.asyncio
async def test_05_reject_nonexistent_restaurant_and_item():
    async with httpx.AsyncClient() as client:
        # Nonexistent restaurant -> 404
        r1 = await client.post(f"{ORDER_URL}/orders", json={
            "restaurant_id": "rest-999",
            "items": [{"menu_item_id": "item-101", "quantity": 1}],
        })
        assert r1.status_code == 404

        # Valid restaurant, wrong item -> 404
        r2 = await client.post(f"{ORDER_URL}/orders", json={
            "restaurant_id": "rest-1",
            "items": [{"menu_item_id": "item-999", "quantity": 1}],
        })
        assert r2.status_code == 404

@pytest.mark.asyncio
async def test_06_twenty_concurrent_orders_unique_ids():
    payload = {
        "restaurant_id": "rest-2",
        "items": [{"menu_item_id": "item-201", "quantity": 1}],
    }
    async with httpx.AsyncClient() as client:
        tasks = [client.post(f"{ORDER_URL}/orders", json=payload) for _ in range(20)]
        responses = await asyncio.gather(*tasks)

    assert all(r.status_code == 201 for r in responses)
    order_ids = {r.json()["order_id"] for r in responses}
    assert len(order_ids) == 20, "All 20 concurrent orders must have unique IDs"