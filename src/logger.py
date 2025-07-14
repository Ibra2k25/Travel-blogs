"""
Logging configuration for TikTok AI Video Bot
"""

import sys
import logging
from pathlib import Path
from typing import Optional
from loguru import logger
from .config import get_settings

def setup_logger(name: Optional[str] = None) -> logging.Logger:
    """Setup and configure loguru logger"""
    settings = get_settings()
    
    # Remove default handler
    logger.remove()
    
    # Ensure log directory exists
    Path(settings.logs_dir).mkdir(parents=True, exist_ok=True)
    
    # Console logging
    if settings.enable_console_logging:
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=settings.log_level,
            colorize=True
        )
    
    # File logging
    if settings.enable_file_logging:
        log_file = Path(settings.log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            str(log_file),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=settings.log_level,
            rotation="10 MB",
            retention="30 days",
            compression="zip"
        )
    
    # Error file logging
    error_log_file = Path(settings.logs_dir) / "errors.log"
    logger.add(
        str(error_log_file),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="5 MB",
        retention="90 days",
        compression="zip"
    )
    
    # Performance logging for debugging
    if settings.debug_mode:
        performance_log_file = Path(settings.logs_dir) / "performance.log"
        logger.add(
            str(performance_log_file),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="5 MB",
            retention="7 days"
        )
    
    # Create standard logging adapter
    class LoguruHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # Find caller from where originated the logged message
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    # Setup standard logging to work with loguru
    logging.basicConfig(handlers=[LoguruHandler()], level=0)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module"""
    return setup_logger(name)

# Performance logging decorator
def log_performance(func):
    """Decorator to log function performance"""
    def wrapper(*args, **kwargs):
        import time
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} executed in {execution_time:.4f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.4f} seconds: {e}")
            raise
    
    return wrapper

# Async performance logging decorator
def log_async_performance(func):
    """Decorator to log async function performance"""
    import asyncio
    import functools
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        import time
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} executed in {execution_time:.4f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.4f} seconds: {e}")
            raise
    
    return wrapper

# Context manager for logging operations
class LogOperation:
    """Context manager for logging operations with timing"""
    
    def __init__(self, operation_name: str, log_level: str = "INFO"):
        self.operation_name = operation_name
        self.log_level = log_level
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        logger.log(self.log_level, f"Starting {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        execution_time = time.time() - self.start_time
        
        if exc_type is None:
            logger.log(self.log_level, f"Completed {self.operation_name} in {execution_time:.4f} seconds")
        else:
            logger.error(f"Failed {self.operation_name} after {execution_time:.4f} seconds: {exc_val}")

# Structured logging helpers
def log_video_generation(
    service: str,
    prompt: str,
    duration: int,
    status: str,
    execution_time: Optional[float] = None,
    error: Optional[str] = None
):
    """Log video generation events with structured data"""
    log_data = {
        "event": "video_generation",
        "service": service,
        "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
        "duration": duration,
        "status": status,
        "execution_time": execution_time,
        "error": error
    }
    
    if status == "success":
        logger.info(f"Video generated successfully", **log_data)
    else:
        logger.error(f"Video generation failed", **log_data)

def log_tiktok_upload(
    username: str,
    video_path: str,
    status: str,
    execution_time: Optional[float] = None,
    error: Optional[str] = None
):
    """Log TikTok upload events with structured data"""
    log_data = {
        "event": "tiktok_upload",
        "username": username,
        "video_path": video_path,
        "status": status,
        "execution_time": execution_time,
        "error": error
    }
    
    if status == "success":
        logger.info(f"Video uploaded to TikTok successfully", **log_data)
    else:
        logger.error(f"TikTok upload failed", **log_data)

def log_scheduler_event(event_type: str, details: dict):
    """Log scheduler events"""
    logger.info(f"Scheduler event: {event_type}", event=event_type, **details)