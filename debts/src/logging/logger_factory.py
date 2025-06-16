from loguru import logger
from .intercept_handler import InterceptHandler
from src.settings import settings
import sys, logging



def setup_logging():
    logger.remove()
    if settings.LOG_TO_CONSOLE:
        format_console = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan> | "
            "<level>{level}</level> | <level>{message}</level>"
        )
        logger.add(sys.stderr, level=settings.LOG_LEVEL.upper(), format=format_console, enqueue=True)
    if settings.LOG_TO_FILE:
        format_file = (
            "{{\"time\":\"{time:YYYY-MM-DDTHH:mm:ss}\","
            "\"level\":\"{level}\",\"module\":\"{module}\","
            "\"message\":\"{message}\"}}"
        )
        logger.add(settings.LOG_FILE, level=settings.LOG_LEVEL.upper(), format=format_file,
                   enqueue=True, rotation="1 week", serialize=True)
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    for mod in settings.INTERCEPT_MODULES:
        logging.getLogger(mod).handlers = [InterceptHandler()]
        logging.getLogger(mod).propagate = False
    return logger

def get_logger():
    return logger