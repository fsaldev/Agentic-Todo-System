"""
Centralized logging for ADW workflows.

Provides dual logging to both stdout (for agent visibility) and file
(for persistence and debugging across sessions).
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class ADWFormatter(logging.Formatter):
    """Custom formatter that includes workflow_id and phase."""

    def __init__(self, workflow_id: str, phase: str):
        self.workflow_id = workflow_id
        self.phase = phase
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] [{self.workflow_id}] [{self.phase}] {record.levelname}: {record.getMessage()}"


def create_logger(
    workflow_id: str,
    phase: str,
    log_dir: Optional[Path] = None,
    level: int = logging.DEBUG,
) -> logging.Logger:
    """Create a logger that writes to both stdout and file.

    Args:
        workflow_id: Unique identifier for the workflow
        phase: Current phase (plan, develop, test, review, document)
        log_dir: Directory for log files. Defaults to .claude/workflows/{workflow_id}/logs/
        level: Logging level (default: DEBUG)

    Returns:
        Configured logger instance
    """
    logger_name = f"adw.{workflow_id}.{phase}"
    logger = logging.getLogger(logger_name)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    logger.setLevel(level)
    formatter = ADWFormatter(workflow_id, phase)

    # Stdout handler - always add for agent visibility
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)

    # File handler - for persistence
    if log_dir is None:
        log_dir = Path(".claude/workflows") / workflow_id / "logs"

    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{phase}.log"

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger(workflow_id: str, phase: str) -> logging.Logger:
    """Get an existing logger or create a new one.

    Args:
        workflow_id: Unique identifier for the workflow
        phase: Current phase

    Returns:
        Logger instance
    """
    logger_name = f"adw.{workflow_id}.{phase}"
    logger = logging.getLogger(logger_name)

    if not logger.handlers:
        return create_logger(workflow_id, phase)

    return logger


def log_section(logger: logging.Logger, title: str) -> None:
    """Log a section header for visual separation.

    Args:
        logger: Logger instance
        title: Section title
    """
    separator = "=" * 50
    logger.info(separator)
    logger.info(f"  {title}")
    logger.info(separator)


def log_step(logger: logging.Logger, step_num: int, description: str) -> None:
    """Log a workflow step.

    Args:
        logger: Logger instance
        step_num: Step number
        description: Step description
    """
    logger.info(f"Step {step_num}: {description}")


def log_success(logger: logging.Logger, message: str) -> None:
    """Log a success message."""
    logger.info(f"SUCCESS: {message}")


def log_error(logger: logging.Logger, message: str) -> None:
    """Log an error message."""
    logger.error(f"ERROR: {message}")
