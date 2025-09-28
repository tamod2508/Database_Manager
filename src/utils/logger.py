"""
Logging configuration for the application with visual indicators and custom log file support
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Dict

from ..config.settings import config

class ColoredFormatter(logging.Formatter):
    """Custom formatter with visual indicators"""
    
    def format(self, record):
        # Add visual indicators based on log level
        if record.levelno >= logging.ERROR:
            record.levelname = f"❌ {record.levelname}"
        elif record.levelno >= logging.WARNING:
            record.levelname = f"⚠️ {record.levelname}"
        elif record.levelno >= logging.INFO:
            # Add success indicators for specific success messages
            if any(word in record.getMessage().lower() for word in
                   ['success', 'completed', 'initialized', 'inserted', 'fetched']):
                record.levelname = f"✅ {record.levelname}"
            else:
                record.levelname = f"ℹ️ {record.levelname}"
        else:  # DEBUG
            record.levelname = f"🔍 {record.levelname}"
        
        return super().format(record)

# Track custom loggers to avoid duplicating handlers
_custom_loggers: Dict[str, logging.Logger] = {}

def setup_logging(level: str = "INFO",
                 log_to_file: bool = True,
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5) -> None:
    """Setup application logging with visual indicators"""
    
    # Create logs directory
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console handler with colored formatter
    console_handler = logging.StreamHandler()
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if enabled) - without emoji for file logs
    if log_to_file:
        log_file = config.LOGS_DIR / "database_manager.log"
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

def get_logger(name: str, log_file_name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance for a module with optional custom log file
    
    Args:
        name: Logger name (usually __name__)
        log_file_name: Optional custom log file name (e.g., "menubar.log")
    
    Returns:
        Configured logger instance
    """
    # Create unique key for custom loggers
    logger_key = f"{name}_{log_file_name}" if log_file_name else name
    
    # Return existing custom logger if already created
    if logger_key in _custom_loggers:
        return _custom_loggers[logger_key]
    
    # Get base logger
    logger = logging.getLogger(name)
    
    # If a custom log file is specified, create a custom logger
    if log_file_name:
        # Create a child logger for the custom file
        custom_logger = logging.getLogger(f"{name}.{log_file_name.replace('.log', '')}")
        custom_logger.setLevel(logging.INFO)
        
        # Prevent propagation to avoid duplicate console logs
        custom_logger.propagate = False
        
        # Add console handler for immediate feedback
        console_handler = logging.StreamHandler()
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        custom_logger.addHandler(console_handler)
        
        # Create custom file handler
        custom_log_file = config.LOGS_DIR / log_file_name
        custom_file_handler = logging.handlers.RotatingFileHandler(
            custom_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        
        # Use same formatter as main file handler (without emoji)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        custom_file_handler.setFormatter(file_formatter)
        custom_logger.addHandler(custom_file_handler)
        
        # Store in cache and return
        _custom_loggers[logger_key] = custom_logger
        return custom_logger
    
    # Return standard logger
    return logger

def create_component_logger(component_name: str) -> logging.Logger:
    """
    Create a logger for a specific component with its own log file
    
    Args:
        component_name: Name of the component (e.g., "menubar", "gui", "core")
    
    Returns:
        Logger that writes to {component_name}.log
    """
    return get_logger(f"database_manager.{component_name}", f"{component_name}.log")

def get_log_files() -> list:
    """
    Get list of all log files in the logs directory
    
    Returns:
        List of log file paths
    """
    if not config.LOGS_DIR.exists():
        return []
    
    return list(config.LOGS_DIR.glob("*.log"))

def clear_old_logs(days_to_keep: int = 30) -> None:
    """
    Clear log files older than specified days
    
    Args:
        days_to_keep: Number of days to keep logs
    """
    import time
    
    if not config.LOGS_DIR.exists():
        return
    
    cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
    
    for log_file in config.LOGS_DIR.glob("*.log*"):
        if log_file.stat().st_mtime < cutoff_time:
            try:
                log_file.unlink()
                print(f"Removed old log file: {log_file.name}")
            except Exception as e:
                print(f"Failed to remove {log_file.name}: {e}")

# Initialize logging on import
setup_logging()