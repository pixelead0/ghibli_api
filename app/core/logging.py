import logging
import sys
from datetime import datetime
from typing import Any, Dict

from app.core.config import settings


class ColorFormatter(logging.Formatter):
    """
    Formateador personalizado que agrega colores a los logs
    """

    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    COLORS = {
        logging.DEBUG: grey,
        logging.INFO: blue,
        logging.WARNING: yellow,
        logging.ERROR: red,
        logging.CRITICAL: bold_red,
    }

    def format(self, record: logging.LogRecord) -> str:
        if not settings.LOG_USE_COLORS:
            return super().format(record)

        color = self.COLORS.get(record.levelno)
        record.levelname = f"{color}{record.levelname}{self.reset}"
        return super().format(record)


def setup_logging() -> None:
    """
    Configura el sistema de logs
    """
    # Crear el logger principal
    logger = logging.getLogger("app")
    logger.setLevel(settings.LOG_LEVEL)

    # Formatador para los logs
    formatter = ColorFormatter(
        fmt=settings.LOG_FORMAT,
        datefmt=settings.LOG_DATE_FORMAT,
    )

    # Handler para la consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler para el archivo
    # file_handler = logging.FileHandler(settings.LOG_FILE)
    # file_handler.setFormatter(formatter)
    # logger.addHandler(file_handler)

    # Evitar la propagación de logs
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger configurado para el módulo especificado
    """
    return logging.getLogger(f"app.{name}")


def log_request_middleware(request: Any) -> Dict[str, Any]:
    """
    Middleware para logear las peticiones HTTP
    """
    logger = get_logger("request")
    timestamp = datetime.now().strftime(settings.LOG_DATE_FORMAT)

    request_data = {
        "timestamp": timestamp,
        "method": request.method,
        "url": str(request.url),
        "client": request.client.host if request.client else None,
        "headers": dict(request.headers),
    }

    logger.info(
        f"Request: {request.method} {request.url} from {request_data['client']}"
    )
    return request_data


def log_response_middleware(response: Any, request_data: Dict[str, Any]) -> None:
    """
    Middleware para logear las respuestas HTTP
    """
    logger = get_logger("response")
    process_time = datetime.now().strftime(settings.LOG_DATE_FORMAT)

    logger.info(
        f"Response: {response.status_code} for {request_data['method']} {request_data['url']}"
    )
