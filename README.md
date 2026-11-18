# Containerized Order and Restaurant Services

A lightweight, two-service microservice system built with **Python 3.12**, **FastAPI**, and **httpx**.

The system consists of:

- **Restaurant Service:** Provides a seeded restaurant and menu catalog.
- **Order Service:** Validates orders through HTTP requests, manages order state, and handles downstream service failures.

Both services run independently in Docker containers and communicate over a user-defined Docker bridge network.

## Architecture

```text
                  Client
                    |
                    | HTTP
                    v
          +--------------------+
          |   Order Service    |
          |    FastAPI :8000   |
          +--------------------+
                    |
                    | HTTP / httpx
                    | X-Correlation-ID
                    v
          +--------------------+
          | Restaurant Service |
          |    FastAPI :8001   |
          +--------------------+
                    |
                    v
             Menu Catalog
             (In-Memory)
```

### Project Structure

```text
food-ordering-system/
├── README.md
├── API_CONTRACT.md
├── tests/
│   └── test_integration.py
└── services/
    ├── restaurant/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── app/
    │       ├── main.py
    │       ├── routes.py
    │       ├── schemas.py
    │       └── store.py
    └── order/
        ├── Dockerfile
        ├── requirements.txt
        └── app/
            ├── main.py
            ├── config.py
            ├── schemas.py
            ├── store.py
            ├── client.py
            └── routes.py
```

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Runtime |
| FastAPI | REST API framework |
| Pydantic | Request and response validation |
| httpx | Asynchronous HTTP communication |
| asyncio | Concurrent request handling |
| Docker | Containerization |
| pytest | Integration testing |

## Key Features

- Independent restaurant and order services.
- Seeded in-memory catalog with 3 restaurants and 7 menu items.
- HTTP-based restaurant and menu validation.
- Asynchronous downstream communication using httpx.
- Configurable HTTP timeout to prevent indefinite waiting.
- `X-Correlation-ID` propagation across service requests.
- Consistent HTTP error handling.
- Thread-safe in-memory order storage using `asyncio.Lock`.
- Support for concurrent order creation.

## Quick Start

### Prerequisites

- Docker installed and running.
- Python 3.12+ (for running integration tests locally).

### 1. Create Docker Network

```bash
docker network create food-net
```

### 2. Build Images

Run from the project root:

```bash
docker build -t restaurant-service:v1 ./services/restaurant

docker build -t order-service:v1 ./services/order
```

### 3. Start Restaurant Service

```bash
docker run -d \
  --name restaurant-service \
  --network food-net \
  -p 8001:8001 \
  restaurant-service:v1
```

### 4. Start Order Service

```bash
docker run -d \
  --name order-service \
  --network food-net \
  -p 8000:8000 \
  -e RESTAURANT_URL=http://restaurant-service:8001 \
  -e HTTP_TIMEOUT_SECONDS=2.0 \
  order-service:v1
```

### 5. Verify Services

```bash
curl http://localhost:8001/healthz

curl http://localhost:8000/healthz
```

Expected response:

```json
{
  "status": "ok",
  "service": "restaurant"
}
```

The Order Service returns the same structure with `"service": "order"`.

## Configuration

The Order Service supports the following environment variables:

| Variable | Default | Description |
|---|---|---|
| `RESTAURANT_URL` | `http://localhost:8001` | Restaurant Service base URL |
| `HTTP_TIMEOUT_SECONDS` | `2.0` | Maximum downstream HTTP timeout |

## API Documentation

Detailed endpoints, request schemas, response examples, and error mappings are documented in:

**[API_CONTRACT.md](./API_CONTRACT.md)**

Interactive API documentation is also available at:

- Order Service: http://localhost:8000/docs
- Restaurant Service: http://localhost:8001/docs

## Integration Testing

Start both Docker containers before running the tests.

Install test dependencies:

```bash
pip install pytest pytest-asyncio httpx
```

Run the integration suite:

```bash
pytest -v
```

### Test Coverage

| Test | Description |
|---|---|
| Health checks | Verifies both services are available |
| Restaurant catalog | Checks seeded restaurants and menu items |
| Order lifecycle | Creates and retrieves an order |
| Invalid requests | Tests malformed and invalid order data |
| Missing entities | Tests unknown restaurants and menu items |
| Concurrent requests | Creates 20 orders concurrently and verifies unique IDs |

## Fault Tolerance Experiment

The Order Service handles downstream failures using a bounded HTTP timeout and maps unavailable dependencies to `503 Service Unavailable`.

Stop the Restaurant Service:

```bash
docker stop restaurant-service
```

Send an order request:

```bash
curl -i -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: outage-demo-001" \
  -d '{
    "restaurant_id": "rest-1",
    "items": [
      {
        "menu_item_id": "item-101",
        "quantity": 1
      }
    ]
  }'
```

Expected response:

```json
{
  "detail": "Restaurant service unavailable"
}
```

Expected HTTP status: `503 Service Unavailable`.

Restore the Restaurant Service:

```bash
docker start restaurant-service
```

Inspect Order Service logs:

```bash
docker logs order-service --tail 20
```

## Limitations

- Data is stored in memory and is lost when a service restarts.
- The system does not include persistent database storage.
- Authentication and authorization are not implemented.
- The services are designed as a foundational microservice demonstration, not a production-ready deployment.

## License

This project is intended for educational and demonstration purposes.