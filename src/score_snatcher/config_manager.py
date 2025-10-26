"""Module for loading the configuration files."""

import csv
import yaml

from typing import Literal
from pathlib import Path
from pydantic import BaseModel, ConfigDict, ValidationError

from src.score_snatcher.constants import CONFIG_PATH, SONG_CONFIG_PATH


class ConfiguredBaseModel(BaseModel):
    """BaseModel class that forbids extra arguments."""

    model_config = ConfigDict(extra="forbid")


class ConfigModel(ConfiguredBaseModel):
    """Config that combines all parameters"""

    class ConfigCategory1(ConfiguredBaseModel):
        """Config for category 1 parameters"""

        float_param: float
        str_param: str

    class ConfigCategory2(ConfiguredBaseModel):
        """Config for category 2 parameters"""

        int_param: int
        bool_param: bool
        list_param: list[str]

    config_category_1: ConfigCategory1
    config_category_two: ConfigCategory2


class SongEntry(BaseModel):
    """BaseModel class for the song configuration file."""

    generate: Literal["TRUE", "FALSE"]
    song: str
    composer: str
    performer: str
    transcriber: str
    url: str


class ConfigManager:
    """Utility class for loading project configuration settings."""

    def __init__(
        self, config_path: Path = CONFIG_PATH, song_config_path: Path = SONG_CONFIG_PATH
    ):
        """ """
        self.config_path = config_path
        self.song_config_path = song_config_path
        self.song_config: list[SongEntry] = []

    def load_config_file(self) -> ConfigModel:
        """ """
        with open(self.config_path) as file:
            config = yaml.safe_load(file)

        return ConfigModel(**config)

    def load_song_csv(self) -> list[SongEntry]:
        """ """
        with open(self.song_config_path, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            entries = []
            for row in reader:
                try:
                    entry = SongEntry(**row)  # type: ignore
                    entries.append(entry)
                except ValidationError as e:
                    print(f"Skipping invalid row: {row}\nError: {e}")

            return entries
