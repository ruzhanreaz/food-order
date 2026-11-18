import os

RESTAURANT_URL: str = os.getenv("RESTAURANT_URL", "http://localhost:8001").rstrip("/")
HTTP_TIMEOUT_SECONDS: float = float(os.getenv("HTTP_TIMEOUT_SECONDS", "2.0"))