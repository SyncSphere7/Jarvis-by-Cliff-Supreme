"""
Advanced Logger for Supreme Jarvis
Provides structured logging, log rotation, and centralized logging capabilities.
"""

import logging
import logging.handlers
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import traceback


class JsonFormatter(logging.Formatter):
    """Custom formatter to output logs in JSON format"""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        # Add extra fields if present
        if hasattr(record, '_extra'):
            log_entry.update(record._extra)
            
        return json.dumps(log_entry)


class AdvancedLogger:
    """Advanced logging system with multiple handlers and structured output"""
    
    def __init__(self, name: str = "supreme_jarvis", log_dir: str = "data/logs"):
        self.name = name
        self.log_dir = log_dir
        self.logger = logging.getLogger(name)
        
        # Create logs directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Set default level
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent adding handlers multiple times
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up file and console handlers"""
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            os.path.join(self.log_dir, f"{self.name}.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(JsonFormatter())
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(JsonFormatter())
        self.logger.addHandler(console_handler)
        
        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            os.path.join(self.log_dir, f"{self.name}_errors.log"),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JsonFormatter())
        self.logger.addHandler(error_handler)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with extra fields"""
        self._log_with_extra(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message with extra fields"""
        self._log_with_extra(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with extra fields"""
        self._log_with_extra(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with extra fields"""
        self._log_with_extra(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with extra fields"""
        self._log_with_extra(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception with traceback"""
        self.logger.error(message, exc_info=True, extra={'_extra': kwargs})
    
    def _log_with_extra(self, level: int, message: str, **kwargs):
        """Log message with extra fields"""
        if kwargs:
            self.logger.log(level, message, extra={'_extra': kwargs})
        else:
            self.logger.log(level, message)
    
    def log_performance(self, operation: str, duration: float, success: bool = True, **kwargs):
        """Log performance metrics"""
        kwargs.update({
            "operation": operation,
            "duration_ms": duration * 1000,
            "success": success
        })
        self.info("Performance metric", **kwargs)
    
    def log_user_action(self, user_id: str, action: str, **kwargs):
        """Log user actions for analytics"""
        kwargs.update({
            "user_id": user_id,
            "action": action
        })
        self.info("User action", **kwargs)
    
    def log_security_event(self, event_type: str, severity: str, **kwargs):
        """Log security events"""
        kwargs.update({
            "event_type": event_type,
            "severity": severity
        })
        self.info("Security event", **kwargs)


# Global logger instance
logger = AdvancedLogger()


def get_logger(name: str = None) -> AdvancedLogger:
    """Get a named logger instance"""
    if name:
        return AdvancedLogger(name)
    return logger