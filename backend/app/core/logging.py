# Logging configuration for the backend.

import logging

# Base logger for the application. Modules import this logger and log
# through it so all output shares one format and level.
logger = logging.getLogger("amucs_nexus")


def configure_logging(level: str = "INFO") -> None:
    """Configure logging to a sensible default for the service."""
    logging.basicConfig(level=level.upper())
