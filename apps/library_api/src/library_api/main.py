from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from observability import StructlogRequestMiddleware, configure_logging, get_logger

from library_api.catalog.api.routers import router as catalog_router
from library_api.lending.api.routers import router as lending_router
from library_api.shared.config import get_settings
from library_api.shared.database import engine
from library_api.shared.exceptions import register_exception_handlers

settings = get_settings()
configure_logging("library_api", level=settings.log_level, json=settings.log_json)
logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("app.startup")
    yield
    await engine.dispose()
    logger.info("app.shutdown")


app = FastAPI(
    title="Library API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)
app.add_middleware(StructlogRequestMiddleware)
register_exception_handlers(app)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(catalog_router)
api_router.include_router(lending_router)
app.include_router(api_router)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
