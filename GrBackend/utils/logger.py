"""
Logger Utility Module

This module provides a centralized logging configuration using loguru.
It sets up structured logging with timestamps, log levels, code line information,
and proper formatting for the entire application.
"""

import sys
from pathlib import Path

from loguru import logger

# Remove default logger
logger.remove()

# Configure loguru logger with custom format
log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

# Add console handler with custom format
logger.add(
    sys.stdout,
    format=log_format,
    level="DEBUG",
    colorize=True,
    backtrace=True,
    diagnose=True,
)

# Add file handler for persistent logging
log_file_path = Path(__file__).parent.parent / "logs" / "application.log"
log_file_path.parent.mkdir(exist_ok=True)

logger.add(
    log_file_path,
    format=log_format,
    level="DEBUG",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    backtrace=True,
    diagnose=True,
)

# Export the configured logger
__all__ = ["logger"]
