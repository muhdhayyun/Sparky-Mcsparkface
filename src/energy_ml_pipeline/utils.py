"""General utility helpers for logging and artifact persistence."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any


def get_logger(name: str = "energy_ml_pipeline") -> logging.Logger:
    """Create or return a package logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def save_json(payload: dict[str, Any], output_path: str | Path) -> Path:
    """Save a JSON payload to disk."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, default=str)
    return output_path
