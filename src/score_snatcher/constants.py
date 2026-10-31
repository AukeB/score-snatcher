"""Module for storing project constants and paths."""

from pathlib import Path

_PACKAGE_DIRECTORY = Path(__file__).resolve().parent
PROJECT_ROOT = _PACKAGE_DIRECTORY.parents[1]

CONFIG_PATH = _PACKAGE_DIRECTORY / "configs" / "config.yaml"
SONG_CONFIG_PATH = _PACKAGE_DIRECTORY / "configs" / "song_config_test.csv"

OUTPUT_DIR_VIDEOS: Path = PROJECT_ROOT / "data" / "videos"
OUTPUT_DIR_SCREENSHOTS: Path = PROJECT_ROOT / "data" / "screenshots"
OUTPUT_DIR_PDFS: Path = PROJECT_ROOT / "data" / "pdfs"
