"""Module for loading the configuration files."""

import csv
import yaml
import logging

from typing import Literal
from pathlib import Path
from pydantic import BaseModel, ConfigDict, ValidationError

from src.score_snatcher.constants import CONFIG_PATH, SONG_CONFIG_PATH


logger = logging.getLogger(__name__)


class ConfiguredBaseModel(BaseModel):
    """BaseModel class that forbids extra arguments."""

    model_config = ConfigDict(extra="forbid")


class SongEntry(ConfiguredBaseModel):
    """BaseModel class for the song CSV configuration."""

    generate: Literal["TRUE", "FALSE"]
    song: str
    composer: str
    performer: str
    transcriber: str
    url: str


class ConfigModel(ConfiguredBaseModel):
    """Main configuration model combining all project parameters."""

    class YoutubeDownloaderConfig(ConfiguredBaseModel):
        """Configuration for YouTube video downloader."""

        output_file_extension: str
        video_quality: str
        ignore_errors: bool
        no_warnings: bool
        extract_flat: bool
        write_subtitles: bool
        write_thumbnail: bool
        write_automatic_sub: bool
        post_processors_key: str
        keep_video: bool
        clean_info_json: bool
        retries: int
        fragment_retries: int
        no_playlist: bool

    youtube_downloader: YoutubeDownloaderConfig


class ConfigManager:
    """Utility class for loading project configuration settings."""

    def __init__(
        self, config_path: Path = CONFIG_PATH, song_config_path: Path = SONG_CONFIG_PATH
    ) -> None:
        """Initializes the ConfigManager with paths to the configuration files.

        Args:
            config_path (Path, optional): Path to the YAML configuration file.
                Defaults to CONFIG_PATH.
            song_config_path (Path, optional): Path to the CSV file containing
                song entries. Defaults to SONG_CONFIG_PATH.
        """
        self.config_path = config_path
        self.song_config_path = song_config_path

    def load_config_file(self) -> ConfigModel:
        """Loads the main YAML configuratioreturnsn file and returns it as a ConfigModel.

        Returns:
            ConfigModel: The loaded configuration as a Pydantic model.
        """
        with open(self.config_path, "r", encoding="utf-8") as file:
            config_dict = yaml.safe_load(file)
        return ConfigModel(**config_dict)

    def load_song_csv(self) -> list[SongEntry]:
        """Loads the song CSV file and returns a list of validated SongEntry objects.

        Rows that fail validation are skipped, and a message is printed for each.

        Returns:
            list[SongEntry]: A list of valid song entries from the CSV file.
        """
        with open(self.song_config_path, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            entries = []
            for row in reader:
                try:
                    entry = SongEntry(**row)  # type: ignore
                    entries.append(entry)
                except ValidationError as e:
                    logger.error(f"Skipping invalid row: {row}\nError: {e}")
        return entries
