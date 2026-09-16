# Logging configuration for the AMUCS Nexus backend.
#
# We use the Python standard library `logging` module.
# - setup_logging() configures the root logger once for the whole process.
# - get_logger() gives each module its own named logger so log lines show
#   which part of the application produced them.

import logging
import sys

LOGGER_NAME = "amucs_nexus"


def setup_logging(level: str = "INFO") -> None:
    """Configure the root logger for the whole application.

    `force=True` replaces any logging config set before import, so the
    application controls the format regardless of startup order.
    """
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout,
        force=True,
    )


def get_logger(name: str = LOGGER_NAME) -> logging.Logger:
    """Return a named logger for a module, e.g. get_logger(__name__)."""
    return logging.getLogger(name)
