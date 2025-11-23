"""Module for testing config_manager.py"""

from src.score_snatcher.config_manager import ConfigModel


def test_load_config_file(mock_config):
    """Testing the 'load_config_file' method."""
    assert isinstance(mock_config, ConfigModel)
    yd = mock_config.youtube_downloader

    assert yd.output_file_extension == ".mp4"
    assert yd.retries == 3