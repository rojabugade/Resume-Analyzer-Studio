import json
import logging
from datetime import UTC, datetime


def get_structured_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()

    class JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            payload = {
                "timestamp": datetime.now(UTC).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
            for key in ("trace_id", "session_id", "user_id"):
                value = getattr(record, key, None)
                if value:
                    payload[key] = value
            return json.dumps(payload)

    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    return logger
