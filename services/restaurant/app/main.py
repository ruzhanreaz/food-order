import logging
import uuid
from fastapi import FastAPI, Request
from app.routes import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [RESTAURANT] %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Restaurant Service")

@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    logger.info(f"correlation_id={correlation_id} method={request.method} path={request.url.path}")
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response

app.include_router(router)