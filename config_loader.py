""" ConfigurationLoader module for PBS Job Monitor & Notifier.

This module handles loading and validating configuration from an external JSON file.
"""

import json
import os
from typing import Dict, Any


class ConfigurationError(Exception):
    """Exception raised for configuration-related errors."""
    pass


class ConfigurationLoader:
    """Loads and manages configuration for the PBS job monitor.

    This class reads configuration from a JSON file, provides default values,
    and validates required parameters.
    """

    # Default configuration values
    DEFAULT_CONFIG = {
        "pbs_username": "zpzheng",
        "poll_interval": 60,
    }

    # Required configuration parameters that must be provided
    REQUIRED_PARAMS = [
        "smtp_server",
        "smtp_port",
        "smtp_user",
        "smtp_password",
        "recipient_email",
    ]

    def __init__(self, config_path: str = "config.json"):
        """Initialize the ConfigurationLoader with a config file path.

        Args:
            config_path: Path to the JSON configuration file. Defaults to "config.json".

        Raises:
            ConfigurationError: If the configuration file does not exist or is invalid.
        """
        # Step 1: Store the configuration file path
        self.config_path = config_path

        # Step 2: Load configuration on initialization
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from the JSON file.

        Returns:
            A dictionary containing the merged configuration.

        Raises:
            ConfigurationError: If the file does not exist or contains invalid JSON.
        """
        # Step 1: Check if the configuration file exists
        if not os.path.exists(self.config_path):
            raise ConfigurationError(
                f"Configuration file not found: {self.config_path}"
            )

        # Step 2: Read and parse the JSON file
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Invalid JSON in configuration file: {e}"
            )

        # Step 3: Merge with default values
        merged_config = self.DEFAULT_CONFIG.copy()
        merged_config.update(loaded_config)

        # Step 4: Validate required parameters
        self._validate_config(merged_config)

        return merged_config

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """Validate that all required configuration parameters are present.

        Args:
            config: The configuration dictionary to validate.

        Raises:
            ConfigurationError: If any required parameter is missing.
        """
        # Step 1: Check for missing required parameters
        missing_params = [
            param for param in self.REQUIRED_PARAMS if param not in config
        ]

        # Step 2: Raise error if any required parameters are missing
        if missing_params:
            raise ConfigurationError(
                f"Missing required configuration parameters: {', '.join(missing_params)}"
            )

    def get(self, key: str, fallback: Any = None) -> Any:
        """Get a configuration value by key.

        Args:
            key: The configuration key to retrieve.
            fallback: The fallback value if the key is not found.

        Returns:
            The configuration value, or fallback if not found.
        """
        # Step 1: Return configuration value with fallback
        return self.config.get(key, fallback)

    @property
    def pbs_username(self) -> str:
        """Get the PBS username.

        Returns:
            The PBS username from configuration.
        """
        return self.config.get("pbs_username", self.DEFAULT_CONFIG["pbs_username"])

    @property
    def smtp_server(self) -> str:
        """Get the SMTP server address.

        Returns:
            The SMTP server address from configuration.
        """
        return self.config["smtp_server"]

    @property
    def smtp_port(self) -> int:
        """Get the SMTP port number.

        Returns:
            The SMTP port number from configuration.
        """
        return int(self.config["smtp_port"])

    @property
    def smtp_user(self) -> str:
        """Get the SMTP username (email address).

        Returns:
            The SMTP username from configuration.
        """
        return self.config["smtp_user"]

    @property
    def smtp_password(self) -> str:
        """Get the SMTP password.

        Returns:
            The SMTP password from configuration.
        """
        return self.config["smtp_password"]

    @property
    def recipient_email(self) -> str:
        """Get the recipient email address.

        Returns:
            The recipient email address from configuration.
        """
        return self.config["recipient_email"]

    @property
    def poll_interval(self) -> int:
        """Get the polling interval in seconds.

        Returns:
            The polling interval from configuration (default: 60).
        """
        return int(self.config.get("poll_interval", self.DEFAULT_CONFIG["poll_interval"]))
