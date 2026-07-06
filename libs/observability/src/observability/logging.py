"""Configuração única de logging estruturado (structlog) para todos os apps do workspace."""

import logging
import sys

import structlog

REQUEST_ID_KEY = "request_id"


def configure_logging(service_name: str, level: str = "INFO", json: bool = True) -> None:
    """Configura structlog + stdlib logging para emitir logs estruturados.

    Deve ser chamada uma única vez, no entrypoint de cada app (`main.py`/`cli.py`).
    """
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level)

    shared_processors: list[structlog.typing.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.CallsiteParameterAdder(
            {structlog.processors.CallsiteParameter.FUNC_NAME}
        ),
    ]

    renderer = structlog.processors.JSONRenderer() if json else structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelNamesMapping().get(level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    structlog.contextvars.bind_contextvars(service=service_name)


def get_logger(*args, **kwargs) -> structlog.stdlib.BoundLogger:
    """Atalho fino sobre `structlog.get_logger`, para manter um único ponto de import."""
    return structlog.get_logger(*args, **kwargs)
