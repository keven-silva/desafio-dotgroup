from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from observability import get_logger

logger = get_logger()


class DomainError(Exception):
    """Base para erros de regra de negócio, mapeados para respostas HTTP apropriadas."""

    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    status_code = status.HTTP_404_NOT_FOUND


class ConflictError(DomainError):
    status_code = status.HTTP_409_CONFLICT


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        logger.warning(
            "domain_error", error_type=type(exc).__name__, message=exc.message, path=request.url.path
        )
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
