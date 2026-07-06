import io
import json
import logging

import structlog

from observability.logging import configure_logging, get_logger


def test_configure_logging_emits_valid_json_with_expected_fields():
    buffer = io.StringIO()
    configure_logging(service_name="test-service", level="INFO", json=True)

    structlog.configure(
        processors=structlog.get_config()["processors"],
        wrapper_class=structlog.get_config()["wrapper_class"],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=buffer),
        cache_logger_on_first_use=False,
    )
    structlog.contextvars.bind_contextvars(service="test-service")

    logger = get_logger()
    logger.info("something.happened", detail="value")

    line = buffer.getvalue().strip()
    payload = json.loads(line)

    assert payload["event"] == "something.happened"
    assert payload["service"] == "test-service"
    assert payload["detail"] == "value"
    assert payload["level"] == "info"
    assert "timestamp" in payload


def test_configure_logging_accepts_console_mode_without_raising():
    configure_logging(service_name="test-service", level="DEBUG", json=False)
    logging.getLogger().info("should not raise")
