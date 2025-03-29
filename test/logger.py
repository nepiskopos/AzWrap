import logging
import os
from config import (
    LOG_FILE,
    LOG_FORMAT,
    LOG_LEVEL
)

INFO = logging.INFO
ERROR = logging.ERROR
WARNING = logging.WARNING

# Configure logging to both file and console
logger = logging.getLogger('AzureSearchManager')
logger.setLevel(logging.getLevelName(LOG_LEVEL))

# Global logging flag
_logging_enabled = True

def enable_logging():
    """Enable logging for AzureSearchManager"""
    global _logging_enabled
    _logging_enabled = True
    log(logging.INFO, "Logging enabled for AzureSearchManager")

def disable_logging():
    """Disable logging for AzureSearchManager"""
    global _logging_enabled
    log(logging.INFO, "Logging disabled for AzureSearchManager")
    _logging_enabled = False

def log(level: int, message: str):
    """Log a message if logging is enabled"""
    if _logging_enabled:
        logger.log(level, message)

# Create formatter
formatter = logging.Formatter(LOG_FORMAT)

# File handler
# Ensure the directory for the log file exists
log_dir = os.path.dirname(LOG_FILE)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Prevent logging from propagating to the root logger
logger.propagate = False