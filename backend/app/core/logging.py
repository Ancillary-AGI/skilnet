"""
Advanced logging configuration for EduVerse platform
"""

import logging
import logging.config
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import os
from pythonjsonlogger import jsonlogger

from app.core.config import settings


class EduVerseFormatter(logging.Formatter):
    """Custom formatter for EduVerse logs"""

    def format(self, record: logging.LogRecord) -> str:
        # Add timestamp if not present
        if not hasattr(record, 'timestamp'):
            record.timestamp = datetime.utcnow().isoformat()

        # Add request ID if available
        if not hasattr(record, 'request_id'):
            record.request_id = 'N/A'

        # Add user ID if available
        if not hasattr(record, 'user_id'):
            record.user_id = 'N/A'

        # Add service name
        record.service = 'eduverse-api'

        # Add environment
        record.environment = os.getenv('ENVIRONMENT', 'development')

        return super().format(record)


class JSONFormatter(jsonlogger.JsonFormatter):
    """JSON formatter for structured logging"""

    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)

        # Add custom fields
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['service'] = 'eduverse-api'
        log_record['environment'] = os.getenv('ENVIRONMENT', 'development')
        log_record['version'] = settings.VERSION

        # Add request context if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        if hasattr(record, 'user_agent'):
            log_record['user_agent'] = record.user_agent
        if hasattr(record, 'ip_address'):
            log_record['ip_address'] = record.ip_address


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[str] = None,
    enable_console: bool = True
) -> None:
    """Setup comprehensive logging configuration"""

    # Create logs directory if it doesn't exist
    if log_file:
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)

    # Configure log levels
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Base configuration
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {},
        'handlers': {},
        'loggers': {
            'eduverse': {
                'level': log_level,
                'handlers': [],
                'propagate': False,
            },
            'uvicorn': {
                'level': log_level,
                'handlers': [],
                'propagate': False,
            },
            'sqlalchemy': {
                'level': 'WARNING',  # Reduce SQLAlchemy noise
                'handlers': [],
                'propagate': False,
            },
        },
        'root': {
            'level': numeric_level,
            'handlers': [],
        }
    }

    # Console handler
    if enable_console:
        if log_format == 'json':
            config['formatters']['json'] = {
                '()': JSONFormatter,
                'format': '%(timestamp)s %(name)s %(levelname)s %(message)s',
            }
            console_formatter = 'json'
        else:
            config['formatters']['console'] = {
                '()': EduVerseFormatter,
                'format': '%(timestamp)s - %(name)s - %(levelname)s - %(request_id)s - %(user_id)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            }
            console_formatter = 'console'

        config['handlers']['console'] = {
            'class': 'logging.StreamHandler',
            'formatter': console_formatter,
            'stream': sys.stdout,
            'level': numeric_level,
        }

        # Add console handler to all loggers
        for logger_name in config['loggers']:
            config['loggers'][logger_name]['handlers'].append('console')
        config['root']['handlers'].append('console')

    # File handler
    if log_file:
        if log_format == 'json':
            file_formatter = 'json'
        else:
            config['formatters']['file'] = {
                '()': EduVerseFormatter,
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(request_id)s - %(user_id)s - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            }
            file_formatter = 'file'

        config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': file_formatter,
            'filename': log_file,
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'level': numeric_level,
        }

        # Add file handler to all loggers
        for logger_name in config['loggers']:
            config['loggers'][logger_name]['handlers'].append('file')
        config['root']['handlers'].append('file')

    # Apply configuration
    logging.config.dictConfig(config)

    # Set up additional loggers
    setup_additional_loggers()


def setup_additional_loggers():
    """Setup additional specialized loggers"""

    # Security logger
    security_logger = logging.getLogger('eduverse.security')
    security_logger.setLevel(logging.INFO)

    # Performance logger
    performance_logger = logging.getLogger('eduverse.performance')
    performance_logger.setLevel(logging.INFO)

    # Audit logger
    audit_logger = logging.getLogger('eduverse.audit')
    audit_logger.setLevel(logging.INFO)

    # Error logger
    error_logger = logging.getLogger('eduverse.error')
    error_logger.setLevel(logging.ERROR)


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance"""
    return logging.getLogger(f'eduverse.{name}')


def log_request_middleware(request, call_next):
    """Middleware for logging HTTP requests"""
    import time
    import uuid

    start_time = time.time()
    request_id = str(uuid.uuid4())

    # Add request ID to logger context
    logger = logging.getLogger('eduverse.request')
    logger = logging.LoggerAdapter(logger, {'request_id': request_id})

    # Log request
    logger.info(
        "Request started",
        extra={
            'method': request.method,
            'url': str(request.url),
            'user_agent': request.headers.get('user-agent', 'N/A'),
            'ip_address': request.client.host if request.client else 'N/A',
        }
    )

    try:
        response = call_next(request)
        process_time = time.time() - start_time

        # Log response
        logger.info(
            "Request completed",
            extra={
                'status_code': response.status_code,
                'process_time': f"{process_time:.3f}s",
            }
        )

        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            "Request failed",
            extra={
                'error': str(e),
                'process_time': f"{process_time:.3f}s",
            },
            exc_info=True
        )
        raise


def log_performance(operation: str, duration: float, **kwargs):
    """Log performance metrics"""
    logger = logging.getLogger('eduverse.performance')
    logger.info(
        f"Performance: {operation}",
        extra={
            'operation': operation,
            'duration': duration,
            'duration_unit': 'seconds',
            **kwargs
        }
    )


def log_security_event(event: str, user_id: Optional[str] = None, **kwargs):
    """Log security-related events"""
    logger = logging.getLogger('eduverse.security')
    logger.warning(
        f"Security: {event}",
        extra={
            'event': event,
            'user_id': user_id or 'N/A',
            **kwargs
        }
    )


def log_audit_event(event: str, user_id: str, resource: str, action: str, **kwargs):
    """Log audit events for compliance"""
    logger = logging.getLogger('eduverse.audit')
    logger.info(
        f"Audit: {event}",
        extra={
            'event': event,
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
    )


def log_error(error: Exception, user_id: Optional[str] = None, **kwargs):
    """Log application errors"""
    logger = logging.getLogger('eduverse.error')
    logger.error(
        f"Error: {str(error)}",
        extra={
            'error_type': type(error).__name__,
            'error_message': str(error),
            'user_id': user_id or 'N/A',
            **kwargs
        },
        exc_info=True
    )


# Initialize logging on import
if settings.DEBUG:
    setup_logging(
        log_level="DEBUG",
        log_format="console",
        enable_console=True
    )
else:
    setup_logging(
        log_level="INFO",
        log_format="json",
        log_file="./logs/eduverse.log",
        enable_console=True
    )
