"""Tests for the config_manager module."""

import logging
from pathlib import Path

import pydantic
import pytest

from score_snatcher.config_manager import ConfigManager
from score_snatcher.config_model import ConfigModel, SongEntry
from tests.conftest import SONG_CSV_HEADER


# Testing the "load_config_file" method from the "ConfigManager" class.


def test_load_config_file_reads_the_default_configuration() -> None:
    config = ConfigManager().load_config_file()

    assert isinstance(config, ConfigModel)
    assert config.youtube_downloader.output_file_extension == "mp4"
    assert config.youtube_downloader.retries == 3


def test_load_config_file_rejects_unknown_keys(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text("youtube_downloader:\n  unknown_key: 1\n", encoding="utf-8")

    with pytest.raises(pydantic.ValidationError):
        ConfigManager(config_path=config_path).load_config_file()


# Testing the "load_song_csv" method from the "ConfigManager" class.


def test_load_song_csv_returns_valid_rows_and_logs_invalid_ones(
    song_csv: Path, caplog: pytest.LogCaptureFixture
) -> None:
    config_manager = ConfigManager(song_config_path=song_csv)

    with caplog.at_level(logging.ERROR, logger="score_snatcher.config_manager"):
        entries = config_manager.load_song_csv()

    assert [entry.song for entry in entries] == ["Aint Misbehaving", "Skipped"]
    entry_types = [type(entry) for entry in entries]

    assert entry_types == [SongEntry, SongEntry]
    assert "Skipping invalid row" in caplog.text


def test_load_song_csv_returns_an_empty_list_for_a_header_only_file(tmp_path: Path) -> None:
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text(SONG_CSV_HEADER + "\n", encoding="utf-8")

    entries = ConfigManager(song_config_path=csv_path).load_song_csv()

    assert entries == []
