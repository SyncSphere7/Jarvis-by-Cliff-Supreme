
import logging
from .advanced_logger import AdvancedLogger

# Create advanced logger instance
logger = AdvancedLogger("supreme_jarvis")

# Compatibility layer for existing code
def get_logger(name: str = None):
    """Get a named logger instance - for compatibility with existing code"""
    return AdvancedLogger(name) if name else logger
