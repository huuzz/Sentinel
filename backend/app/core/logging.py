import logging
from logging.config import dictConfig

from app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "pythonjsonlogger.json.JsonFormatter",
                    "format": "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s",
                    "defaults": {"request_id": None},
                }
            },
            "handlers": {"default": {"class": "logging.StreamHandler", "formatter": "json"}},
            "root": {"handlers": ["default"], "level": settings.log_level.upper()},
        }
    )
    logging.getLogger(__name__).info("logging_configured")
