""" Logger module for PBS Job Monitor & Notifier.

This module provides centralized logging configuration and functions.
"""

import logging
import os
from datetime import datetime
from typing import Optional


class LoggerConfig:
    """Centralized logger configuration for the application.

    This class configures and provides logger instances with consistent
    formatting and output destinations.
    """

    _log_dir = "logs"
    _initialized = False

    @classmethod
    def setup(cls, name: str = "pbs_monitor",
              log_file: Optional[str] = None,
              level: int = logging.INFO) -> logging.Logger:
        """Setup and return a configured logger.

        Args:
            name: The name of the logger.
            log_file: Optional custom log file path. If None, uses default.
            level: Logging level (default: INFO).

        Returns:
            A configured logging.Logger instance.
        """
        # Step 1: Check if logger already exists
        logger = logging.getLogger(name)
        if logger.handlers:
            return logger

        # Step 2: Set logger level and propagate
        logger.setLevel(level)
        logger.propagate = False

        # Step 3: Create log formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Step 4: Determine log file path
        if log_file is None:
            log_file = os.path.join(
                cls._log_dir,
                f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
            )

        # Step 5: Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        # Step 6: Add file handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Step 7: Add console handler for visibility
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Step 8: Log initialization
        logger.info(f"Logger initialized: {log_file}")

        return logger

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get an existing logger or setup a new one.

        Args:
            name: The name of the logger.

        Returns:
            A logging.Logger instance.
        """
        logger = logging.getLogger(name)
        if not logger.handlers:
            return cls.setup(name)
        return logger
