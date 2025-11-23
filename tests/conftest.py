"""Module conftest.py, reusable code for pytest."""

import pytest
from unittest.mock import patch, mock_open
from pathlib import Path

from src.score_snatcher.config_manager import ConfigManager


@pytest.fixture(scope="function", name="mock_yaml_content")
def mock_yaml_config():
    """Fixture that defines a mock config content"""
    yaml_content = """
        youtube_downloader:
            output_file_extension: '.mp4'
            video_quality: 'bestvideo[height<=1080]'
            ignore_errors: false
            no_warnings: false
            extract_flat: false
            write_subtitles: false
            write_thumbnail: false
            write_automatic_sub: false
            post_processors_key: "FFmpegVideoConvertor"
            keep_video: false
            clean_info_json: true
            retries: 3
            fragment_retries: 3
            no_playlist: true
    """

    return yaml_content


@pytest.fixture(scope="function", name="mock_config")
def test_load_config_file(mock_yaml_content):
    """Test loading config using mocked open."""
    m_open = mock_open(read_data=mock_yaml_content)

    # Patch built-in open inside config_manager module
    with patch("src.score_snatcher.config_manager.open", m_open):
        config_manager = ConfigManager(Path("mock_config_path.yaml"))
        config = config_manager.load_config_file()

    return config