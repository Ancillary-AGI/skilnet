"""
Logging configuration for EduVerse platform
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        if hasattr(record, 'ip_address'):
            log_entry["ip_address"] = record.ip_address
            
        return json.dumps(log_entry)


def setup_logging(
    log_level: str = "INFO",
    log_file: str = "logs/eduverse.log",
    enable_json: bool = False
) -> None:
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Define formatters
    formatters = {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "json": {
            "()": JSONFormatter
        }
    }
    
    # Define handlers
    handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "json" if enable_json else "default",
            "stream": sys.stdout
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "json" if enable_json else "detailed",
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "json" if enable_json else "detailed",
            "filename": "logs/eduverse_errors.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8"
        }
    }
    
    # Define loggers
    loggers = {
        "": {  # Root logger
            "level": log_level,
            "handlers": ["console", "file", "error_file"]
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "uvicorn.error": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["file"],
            "propagate": False
        },
        "sqlalchemy.engine": {
            "level": "WARNING",
            "handlers": ["file"],
            "propagate": False
        },
        "app": {
            "level": log_level,
            "handlers": ["console", "file", "error_file"],
            "propagate": False
        }
    }
    
    # Configure logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "handlers": handlers,
        "loggers": loggers
    }
    
    logging.config.dictConfig(logging_config)
    
    # Set up custom logger for the app
    logger = logging.getLogger("app")
    logger.info("Logging system initialized")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(f"app.{name}")


class LoggerMixin:
    """Mixin class to add logging capabilities to any class"""
    
    @property
    def logger(self) -> logging.Logger:
        return get_logger(self.__class__.__name__)


# Context manager for request logging
class RequestLogger:
    """Context manager for request-specific logging"""
    
    def __init__(self, request_id: str, user_id: str = None, ip_address: str = None):
        self.request_id = request_id
        self.user_id = user_id
        self.ip_address = ip_address
        self.logger = get_logger("request")
        
    def __enter__(self):
        self.logger.info(
            f"Request started: {self.request_id}",
            extra={
                "request_id": self.request_id,
                "user_id": self.user_id,
                "ip_address": self.ip_address
            }
        )
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.logger.error(
                f"Request failed: {self.request_id} - {exc_val}",
                extra={
                    "request_id": self.request_id,
                    "user_id": self.user_id,
                    "ip_address": self.ip_address
                },
                exc_info=True
            )
        else:
            self.logger.info(
                f"Request completed: {self.request_id}",
                extra={
                    "request_id": self.request_id,
                    "user_id": self.user_id,
                    "ip_address": self.ip_address
                }
            )


# Performance logging decorator
def log_performance(func):
    """Decorator to log function performance"""
    import functools
    import time
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        logger = get_logger("performance")
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(
                f"{func.__name__} completed in {execution_time:.3f}s",
                extra={"execution_time": execution_time, "function": func.__name__}
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {execution_time:.3f}s: {e}",
                extra={"execution_time": execution_time, "function": func.__name__},
                exc_info=True
            )
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        logger = get_logger("performance")
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(
                f"{func.__name__} completed in {execution_time:.3f}s",
                extra={"execution_time": execution_time, "function": func.__name__}
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {execution_time:.3f}s: {e}",
                extra={"execution_time": execution_time, "function": func.__name__},
                exc_info=True
            )
            raise
    
    # Return appropriate wrapper based on function type
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper