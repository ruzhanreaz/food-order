# API Contract

This document describes the REST API contracts for the Restaurant Service and Order Service.

## Base URLs

| Service | Base URL |
|---|---|
| Restaurant Service | `http://localhost:8001` |
| Order Service | `http://localhost:8000` |

All request and response bodies use JSON.

---

# 1. Restaurant Service

Provides restaurant information and menu catalogs.

## GET `/healthz`

Checks service availability.

**Response: `200 OK`**

```json
{
  "status": "ok",
  "service": "restaurant"
}
```

## GET `/restaurants`

Returns the seeded restaurant catalog.

**Response: `200 OK`**

```json
[
  {
    "id": "rest-1",
    "name": "Dhaka Spice House",
    "cuisine": "Bengali",
    "menu": [
      {
        "id": "item-101",
        "name": "Kacchi Biryani",
        "price": 12.5
      },
      {
        "id": "item-102",
        "name": "Beef Tehari",
        "price": 9.0
      },
      {
        "id": "item-103",
        "name": "Borhani",
        "price": 2.5
      }
    ]
  }
]
```

The catalog contains 3 restaurants and 7 menu items.

## GET `/restaurants/{restaurant_id}`

Returns a restaurant and its menu by ID.

**Example:**

```http
GET /restaurants/rest-1
```

**Response: `200 OK`**

Returns the matching restaurant object.

**Error: `404 Not Found`**

```json
{
  "detail": "Restaurant not found"
}
```

---

# 2. Order Service

Validates incoming orders against the Restaurant Service and stores confirmed orders.

## GET `/healthz`

Checks service availability.

**Response: `200 OK`**

```json
{
  "status": "ok",
  "service": "order"
}
```

## POST `/orders`

Creates a new order.

### Request Headers

| Header | Required | Description |
|---|---|---|
| `Content-Type` | Yes | `application/json` |
| `X-Correlation-ID` | No | Request tracing identifier |

If a correlation ID is not provided, the service generates one.

### Request Body

```json
{
  "restaurant_id": "rest-1",
  "items": [
    {
      "menu_item_id": "item-101",
      "quantity": 2
    }
  ]
}
```

### Request Fields

| Field | Type | Validation |
|---|---|---|
| `restaurant_id` | String | Must reference an existing restaurant |
| `items` | Array | Must contain valid order items |
| `menu_item_id` | String | Must reference an item in the selected restaurant |
| `quantity` | Integer | Must be greater than zero |

### Success Response: `201 Created`

```json
{
  "order_id": "ord-9a4f12c8e01b",
  "correlation_id": "demo-req-101",
  "restaurant_id": "rest-1",
  "items": [
    {
      "menu_item_id": "item-101",
      "quantity": 2
    }
  ],
  "status": "CONFIRMED",
  "created_at": "2026-11-19T10:15:30.123456Z"
}
```

The response contains:

- A unique order ID.
- The request correlation ID.
- The selected restaurant.
- The ordered menu items and quantities.
- The order status.
- The order creation timestamp.

### Example cURL

```bash
curl -i -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: demo-req-101" \
  -d '{
    "restaurant_id": "rest-1",
    "items": [
      {
        "menu_item_id": "item-101",
        "quantity": 2
      }
    ]
  }'
```

## GET `/orders/{order_id}`

Retrieves an existing order by ID.

**Example:**

```http
GET /orders/ord-9a4f12c8e01b
```

**Response: `200 OK`**

Returns the stored order object using the same schema as the creation response.

**Error: `404 Not Found`**

```json
{
  "detail": "Order not found"
}
```

---

# 3. Error Handling

The Order Service maps validation and downstream failures to consistent HTTP status codes.

| HTTP Status | Error | Scenario |
|---|---|---|
| `400 Bad Request` | Invalid request | Malformed JSON, missing required fields, or invalid quantity |
| `404 Not Found` | Resource not found | Unknown restaurant, menu item, or order |
| `503 Service Unavailable` | Dependency unavailable | Restaurant Service unreachable or request timeout |

### Example: Invalid Quantity

**Request:**

```json
{
  "restaurant_id": "rest-1",
  "items": [
    {
      "menu_item_id": "item-101",
      "quantity": 0
    }
  ]
}
```

**Response: `400 Bad Request`**

### Example: Unknown Restaurant

**Response: `404 Not Found`**

```json
{
  "detail": "Restaurant not found"
}
```

### Example: Restaurant Service Unavailable

**Response: `503 Service Unavailable`**

```json
{
  "detail": "Restaurant service unavailable"
}
```

---

# 4. Correlation ID Propagation

The `X-Correlation-ID` header enables request tracing across services.

Expected behavior:

1. The client sends an `X-Correlation-ID` header.
2. The Order Service extracts or generates the correlation ID.
3. The Order Service forwards it to the Restaurant Service.
4. Both services include it in their request logs and response headers.
5. The Order Service includes it in the created order response.

Example:

```http
X-Correlation-ID: demo-req-101
```

---

# 5. Downstream Timeout Handling

The Order Service uses `httpx` with a configurable timeout.

Default configuration:

```env
RESTAURANT_URL=http://restaurant-service:8001
HTTP_TIMEOUT_SECONDS=2.0
```

If the Restaurant Service becomes unreachable or exceeds the configured timeout, the Order Service returns:

```http
503 Service Unavailable
```

```json
{
  "detail": "Restaurant service unavailable"
}
```

This prevents requests from waiting indefinitely for the downstream dependency.

---

# 6. Order Concurrency

Order state is maintained in an in-memory store protected by `asyncio.Lock`.

This ensures that concurrent order creation and retrieval operations are safely coordinated within the running Order Service process.

**Note:** The in-memory implementation does not provide persistence across restarts or shared state across multiple service replicas.