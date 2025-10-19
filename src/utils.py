"""Utility module for file and directory management."""

from pathlib import Path
import logging


def create_output_directories() -> None:
    """Create 'data' and its subdirectories for program outputs."""
    dir_path_root = Path(__file__).resolve().parent.parent
    sub_dirs = ["data/videos", "data/screenshots", "data/pdfs"]

    for sub_dir in sub_dirs:
        (dir_path_root / sub_dir).mkdir(parents=True, exist_ok=True)

    logging.info("✅ Output directories created or already existed.")
