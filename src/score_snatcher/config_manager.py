"""Module for loading the score-snatcher configuration files."""

import csv
import logging
from pathlib import Path

import yaml
from pydantic import ValidationError

from score_snatcher.config_model import ConfigModel, SongEntry
from score_snatcher.constants import CONFIG_PATH, SONG_CONFIG_PATH

logger = logging.getLogger(__name__)


class ConfigManager:
    """Load the YAML settings and the song CSV file.

    Attributes:
        config_path (Path): Path to the YAML configuration file.
        song_config_path (Path): Path to the CSV file with the song entries.

    Example:
        >>> config_manager = ConfigManager()
        >>> config = config_manager.load_config_file()
        >>> songs = config_manager.load_song_csv()
    """

    def __init__(
        self,
        config_path: Path = CONFIG_PATH,
        song_config_path: Path = SONG_CONFIG_PATH,
    ) -> None:
        """Store the paths to the configuration files.

        Args:
            config_path (Path): Path to the YAML configuration file.
            song_config_path (Path): Path to the CSV file with the song entries.
        """

        self.config_path = config_path
        self.song_config_path = song_config_path

    def load_config_file(self) -> ConfigModel:
        """Read the YAML configuration file and validate it.

        Returns:
            config (ConfigModel): The validated configuration.
        """

        with open(self.config_path, encoding="utf-8") as file:
            raw_config = yaml.safe_load(file)

        config = ConfigModel.model_validate(raw_config)

        return config

    def load_song_csv(self) -> list[SongEntry]:
        """Read the song CSV file and validate every row.

        Rows that fail validation are logged and skipped.

        Returns:
            entries (list[SongEntry]): The valid song entries, in file order.
        """

        entries: list[SongEntry] = []

        with open(self.song_config_path, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    entry = SongEntry.model_validate(row)
                    entries.append(entry)

                except ValidationError as error:
                    logger.error(f"Skipping invalid row: {row}\nError: {error}")

        return entries
