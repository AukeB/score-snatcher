"""Tests for the youtube_downloader module."""

import logging
from pathlib import Path

import pytest

from score_snatcher.config_model import ConfigModel
from score_snatcher.youtube_downloader import YoutubeDownloader
from tests.conftest import _FakeYoutubeDL


def _make_downloader(output_dir: Path, url: str = "https://www.youtube.com/watch?v=abc") -> YoutubeDownloader:
    """Create a downloader with the default configuration.

    Args:
        output_dir (Path): Folder for the downloads.
        url (str): The video URL to work with.

    Returns:
        downloader (YoutubeDownloader): The downloader.
    """

    downloader = YoutubeDownloader(output_dir_path=output_dir, url=url)

    return downloader


# Testing the "__init__" method from the "YoutubeDownloader" class.


def test_init_reads_the_video_title(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL]
) -> None:
    fake_ytdl.info = {"title": "Aint Misbehaving"}

    downloader = _make_downloader(output_dir=tmp_path)

    assert downloader.video_title == "Aint Misbehaving"
    assert isinstance(downloader.config_youtube_download, ConfigModel.YoutubeDownloaderConfig)


# Testing the "_construct_ydl_opts_dict" method from the "YoutubeDownloader" class.


def test_construct_ydl_opts_maps_settings_to_yt_dlp_options(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL]
) -> None:
    fake_ytdl.info = {"title": "x"}
    downloader = _make_downloader(output_dir=tmp_path)

    options = downloader._construct_ydl_opts_dict()

    assert options["format"] == "bestvideo[height<=1080]"
    assert options["noplaylist"] is True
    assert options["postprocessors"][0]["preferedformat"] == "mp4"


# Testing the "_obtain_video_title" method from the "YoutubeDownloader" class.


def test_obtain_video_title_returns_unknown_when_no_info(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL], caplog: pytest.LogCaptureFixture
) -> None:
    fake_ytdl.info = None

    with caplog.at_level(logging.ERROR, logger="score_snatcher.youtube_downloader"):
        downloader = _make_downloader(output_dir=tmp_path)

    assert downloader.video_title == "Unknown"
    assert "Failed to extract video information" in caplog.text


def test_obtain_video_title_returns_unknown_when_title_is_missing(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL]
) -> None:
    fake_ytdl.info = {"id": "abc"}

    downloader = _make_downloader(output_dir=tmp_path)

    assert downloader.video_title == "Unknown"


def test_obtain_video_title_returns_unknown_when_title_is_not_text(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL]
) -> None:
    fake_ytdl.info = {"title": 42}

    downloader = _make_downloader(output_dir=tmp_path)

    assert downloader.video_title == "Unknown"


def test_obtain_video_title_logs_errors_from_yt_dlp(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL], caplog: pytest.LogCaptureFixture
) -> None:
    fake_ytdl.info = {"raise": True}

    with caplog.at_level(logging.ERROR, logger="score_snatcher.youtube_downloader"):
        downloader = _make_downloader(output_dir=tmp_path)

    assert downloader.video_title == "Unknown"
    assert "network down" in caplog.text


# Testing the "download_video" method from the "YoutubeDownloader" class.


def test_download_video_sets_the_output_template(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL]
) -> None:
    fake_ytdl.info = {"title": "x"}
    downloader = _make_downloader(output_dir=tmp_path)

    downloader.download_video(output_file_name="my_video")

    assert downloader.ydl_opts["outtmpl"] == f"{tmp_path / 'my_video'}.%(ext)s"


def test_download_video_logs_failures(
    tmp_path: Path,
    fake_ytdl: type[_FakeYoutubeDL],
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_ytdl.info = {"title": "x"}
    downloader = _make_downloader(output_dir=tmp_path)

    def failing_download(self: _FakeYoutubeDL, urls: list[str]) -> None:
        raise RuntimeError("disk full")

    monkeypatch.setattr(fake_ytdl, "download", failing_download)

    with caplog.at_level(logging.ERROR, logger="score_snatcher.youtube_downloader"):
        downloader.download_video(output_file_name="my_video")

    assert "disk full" in caplog.text


def test_download_video_calls_yt_dlp_with_the_url(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL]
) -> None:
    fake_ytdl.info = {"title": "x"}
    downloader = _make_downloader(output_dir=tmp_path)
    recorded: list[str] = []

    def record_download(self: _FakeYoutubeDL, urls: list[str]) -> None:
        recorded.extend(urls)

    fake_ytdl.download = record_download  # type: ignore[method-assign]

    downloader.download_video(output_file_name="my_video")

    assert recorded == ["https://www.youtube.com/watch?v=abc"]


# Testing the "_channel_name_to_url" method from the "YoutubeDownloader" class.


@pytest.mark.parametrize(
    ("channel_name", "expected"),
    [
        ("@handle", "https://www.youtube.com/@handle"),
        ("UCabc123", "https://www.youtube.com/channel/UCabc123"),
        ("https://www.youtube.com/c/name", "https://www.youtube.com/c/name"),
        ("LegacyName", "https://www.youtube.com/c/LegacyName"),
    ],
)
def test_channel_name_to_url_handles_every_form(channel_name: str, expected: str) -> None:
    assert YoutubeDownloader._channel_name_to_url(channel_name=channel_name) == expected


# Testing the "_to_watch_url" method from the "YoutubeDownloader" class.


def test_to_watch_url_builds_a_url_from_a_bare_id() -> None:
    assert YoutubeDownloader._to_watch_url(video_url="abc") == "https://www.youtube.com/watch?v=abc"


def test_to_watch_url_keeps_full_urls() -> None:
    url = "https://www.youtube.com/watch?v=abc"

    assert YoutubeDownloader._to_watch_url(video_url=url) == url


# Testing the "_make_safe_title" method from the "YoutubeDownloader" class.


def test_make_safe_title_removes_unsafe_characters() -> None:
    safe = YoutubeDownloader._make_safe_title(video_title="  Song: Part/1 (Live)?  ")

    assert safe == "Song Part1 (Live)"


# Testing the "download_all_videos_from_channel" method from the "YoutubeDownloader" class.


def test_download_all_videos_updates_url_and_title_for_each_entry(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL]
) -> None:
    fake_ytdl.info = {"title": "x"}
    downloader = _make_downloader(output_dir=tmp_path)

    fake_ytdl.info = {
        "entries": [
            {"url": "abc", "title": "First: Song?"},
            {"url": "https://www.youtube.com/watch?v=def", "title": "Second"},
            {"title": "No url"},
            {"url": "ghi"},
        ]
    }

    downloader.download_all_videos_from_channel(channel_name="@handle")

    assert downloader.url == "https://www.youtube.com/watch?v=ghi"
    assert downloader.video_title == "UnknownTitle"


def test_download_all_videos_logs_when_channel_info_is_missing(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL], caplog: pytest.LogCaptureFixture
) -> None:
    fake_ytdl.info = {"title": "x"}
    downloader = _make_downloader(output_dir=tmp_path)
    fake_ytdl.info = None

    with caplog.at_level(logging.ERROR, logger="score_snatcher.youtube_downloader"):
        downloader.download_all_videos_from_channel(channel_name="@handle")

    assert "Could not fetch channel info" in caplog.text


def test_download_all_videos_logs_when_channel_has_no_entries(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL], caplog: pytest.LogCaptureFixture
) -> None:
    fake_ytdl.info = {"title": "x"}
    downloader = _make_downloader(output_dir=tmp_path)
    fake_ytdl.info = {"entries": []}

    with caplog.at_level(logging.ERROR, logger="score_snatcher.youtube_downloader"):
        downloader.download_all_videos_from_channel(channel_name="@handle")

    assert "No videos found" in caplog.text


def test_download_all_videos_logs_errors_from_yt_dlp(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL], caplog: pytest.LogCaptureFixture
) -> None:
    fake_ytdl.info = {"title": "x"}
    downloader = _make_downloader(output_dir=tmp_path)
    fake_ytdl.info = {"raise": True}

    with caplog.at_level(logging.ERROR, logger="score_snatcher.youtube_downloader"):
        downloader.download_all_videos_from_channel(channel_name="@handle")

    assert "Error while listing channel videos" in caplog.text
