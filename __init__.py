"""PBS Job Monitor & Notifier.

A command-line tool that wraps the PBS qsub command and automatically
monitors job status, sending email notifications when jobs complete.
"""

from config_loader import ConfigurationLoader, ConfigurationError
from monitor import JobMonitor
from notifier import EmailNotifier

__version__ = "0.1.0"
__author__ = "CCMG"
__all__ = [
    "ConfigurationLoader",
    "ConfigurationError",
    "JobMonitor",
    "EmailNotifier",
]
