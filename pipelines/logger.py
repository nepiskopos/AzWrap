import os
import sys
import logging
import codecs
from typing import List, Optional

class LoggerSetup:
    """
    A utility class to configure and set up logging throughout the application.
    Handles console and file logging with customized formatting.
    """
    
    @staticmethod
    def setup_logger(
        logger_name: str,
        log_level: int = logging.INFO,
        log_file: Optional[str] = None,
        log_dir: Optional[str] = None,
        propagate: bool = False,
        formatter_pattern: str = '%(asctime)s - %(levelname)s - %(message)s',
        suppress_azure_loggers: bool = True
    ) -> logging.Logger:
        """
        Set up a logger with console and optional file handlers.
        
        Args:
            logger_name: Name of the logger to create
            log_level: Logging level (default: INFO)
            log_file: Optional log file name. If None, no file handler is created
            log_dir: Directory to store log files. If provided with log_file, ensures directory exists
            propagate: Whether the logger should propagate to parent loggers
            formatter_pattern: Format string for log entries
            suppress_azure_loggers: Whether to suppress Azure SDK related loggers
            
        Returns:
            Configured logger instance
        """
        # Create logs directory if needed
        if log_file and log_dir:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            log_file_path = os.path.join(log_dir, log_file)
        elif log_file:
            log_file_path = log_file
        else:
            log_file_path = None
        
        # Set stdout/stderr encoding to utf-8 to handle non-ASCII characters
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')
        
        # Configure main logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        
        # Clear existing handlers if any
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Create formatter
        formatter = logging.Formatter(formatter_pattern)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Create file handler if specified
        if log_file_path:
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        # Set propagation
        logger.propagate = propagate
        
        # Suppress Azure SDK related loggers if requested
        if suppress_azure_loggers:
            LoggerSetup.suppress_azure_loggers()
        
        return logger
    
    @staticmethod
    def suppress_azure_loggers(log_level: int = logging.WARNING) -> None:
        """
        Suppress verbose output from Azure SDK related loggers.
        
        Args:
            log_level: Level to set for Azure loggers (default: WARNING)
        """
        azure_loggers = [
            'azure',
            'azure.core',
            'azure.identity',
            'azure.mgmt',
            'azure.storage',
            'azure.search',
            'msal',
            'urllib3',
            'requests'
        ]
        
        for azure_logger in azure_loggers:
            logging.getLogger(azure_logger).setLevel(log_level)

# Default logger factory function for easier access
def get_logger(
    logger_name: str = "application",
    log_file: Optional[str] = None,
    log_dir: Optional[str] = None
) -> logging.Logger:
    """
    Get a configured logger instance with default settings.
    
    Args:
        logger_name: Name for the logger
        log_file: Optional log file name
        log_dir: Optional directory for log files
        
    Returns:
        Configured logger instance
    """
    if log_dir is None and log_file is not None:
        # Default to 'logs' subdirectory in current directory
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    
    return LoggerSetup.setup_logger(
        logger_name=logger_name,
        log_level=logging.INFO,
        log_file=log_file,
        log_dir=log_dir
    )