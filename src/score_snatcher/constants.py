"""Module containing global constants."""

from pathlib import Path

CONFIG_PATH = Path("src/score_snatcher/configs/config.yaml")
SONG_CONFIG_PATH = Path("src/score_snatcher/configs/song_config_test.csv")

OUTPUT_DIR_VIDEOS_REL_PATH: str = "data/videos"
OUTPUT_DIR_SCREENSHOTS_REL_PATH: str = "data/screenshots"
OUTPUT_DIR_PDFS_REL_PATH: str = "data/pdfs"

YT_DLP_DOWNLOAD_FORMAT: str = "bestvideo[ext=mp4]/bestvideo"
