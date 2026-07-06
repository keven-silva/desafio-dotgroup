from fastapi import FastAPI
from observability import StructlogRequestMiddleware, configure_logging, get_logger

from rag.api.routers import router
from rag.core.config import get_settings

settings = get_settings()
configure_logging("rag", level=settings.log_level, json=settings.log_json)
logger = get_logger()

app = FastAPI(title="RAG Service", version="0.1.0")
app.add_middleware(StructlogRequestMiddleware)
app.include_router(router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
