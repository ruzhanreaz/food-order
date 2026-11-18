from contextlib import asynccontextmanager
import logging
import uuid
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.client import restaurant_client
from app.routes import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [ORDER] %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await restaurant_client.close()

app = FastAPI(title="Order Service", lifespan=lifespan)

# Map Pydantic validation errors (bad quantities, missing fields, invalid JSON) to HTTP 400
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": "Malformed input or invalid field values", "errors": exc.errors()},
    )

@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.correlation_id = correlation_id
    logger.info(f"correlation_id={correlation_id} method={request.method} path={request.url.path}")
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response

app.include_router(router)