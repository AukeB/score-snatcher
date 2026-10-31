"""Tests for the youtube_downloader module."""

import logging
from pathlib import Path
from typing import Any

import pytest

from score_snatcher.config_model import ConfigModel
from score_snatcher.youtube_downloader import YoutubeDownloader
from tests.conftest import _FakeYoutubeDL


def _make_downloader(output_dir: Path) -> YoutubeDownloader:
    """Create a downloader with the default configuration.

    Args:
        output_dir (Path): Folder for the downloads.

    Returns:
        downloader (YoutubeDownloader): The downloader.
    """

    downloader = YoutubeDownloader(output_dir_path=output_dir)

    return downloader


# Testing the "__init__" method from the "YoutubeDownloader" class.


def test_init_loads_the_download_settings(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL]
) -> None:
    downloader = _make_downloader(output_dir=tmp_path)

    assert isinstance(downloader.config_youtube_download, ConfigModel.YoutubeDownloaderConfig)


def test_init_creates_the_output_folder_when_missing(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL]
) -> None:
    output_dir = tmp_path / "videos"

    _make_downloader(output_dir=output_dir)

    assert output_dir.is_dir()


# Testing the "_construct_ydl_opts_dict" method from the "YoutubeDownloader" class.


def test_construct_ydl_opts_maps_settings_to_yt_dlp_options(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL]
) -> None:
    downloader = _make_downloader(output_dir=tmp_path)

    options = downloader._construct_ydl_opts_dict()

    assert options["format"] == "bestvideo[height<=1080]"
    assert options["noplaylist"] is True
    assert options["postprocessors"][0]["preferedformat"] == "mp4"


# Testing the "obtain_video_title" method from the "YoutubeDownloader" class.


def test_obtain_video_title_returns_the_title(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL]
) -> None:
    fake_ytdl.info = {"title": "Aint Misbehaving"}
    downloader = _make_downloader(output_dir=tmp_path)

    video_title = downloader.obtain_video_title(url="https://www.youtube.com/watch?v=abc")

    assert video_title == "Aint Misbehaving"


def test_obtain_video_title_returns_unknown_when_no_info(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL], caplog: pytest.LogCaptureFixture
) -> None:
    fake_ytdl.info = None
    downloader = _make_downloader(output_dir=tmp_path)

    with caplog.at_level(logging.ERROR, logger="score_snatcher.youtube_downloader"):
        video_title = downloader.obtain_video_title(url="https://www.youtube.com/watch?v=abc")

    assert video_title == "Unknown"
    assert "Failed to extract video information" in caplog.text


def test_obtain_video_title_returns_unknown_when_title_is_missing(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL]
) -> None:
    fake_ytdl.info = {"id": "abc"}
    downloader = _make_downloader(output_dir=tmp_path)

    video_title = downloader.obtain_video_title(url="https://www.youtube.com/watch?v=abc")

    assert video_title == "Unknown"


def test_obtain_video_title_returns_unknown_when_title_is_not_text(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL]
) -> None:
    fake_ytdl.info = {"title": 42}
    downloader = _make_downloader(output_dir=tmp_path)

    video_title = downloader.obtain_video_title(url="https://www.youtube.com/watch?v=abc")

    assert video_title == "Unknown"


def test_obtain_video_title_logs_errors_from_yt_dlp(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL], caplog: pytest.LogCaptureFixture
) -> None:
    fake_ytdl.info = {"raise": True}
    downloader = _make_downloader(output_dir=tmp_path)

    with caplog.at_level(logging.ERROR, logger="score_snatcher.youtube_downloader"):
        video_title = downloader.obtain_video_title(url="https://www.youtube.com/watch?v=abc")

    assert video_title == "Unknown"
    assert "network down" in caplog.text


# Testing the "download_video" method from the "YoutubeDownloader" class.


def test_download_video_extracts_the_info_once_without_downloading(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL], monkeypatch: pytest.MonkeyPatch
) -> None:
    extracted: list[tuple[str, bool]] = []

    def record_extract(
        self: _FakeYoutubeDL, url: str, download: bool = True
    ) -> dict[str, Any]:
        extracted.append((url, download))

        return {"title": "x"}

    monkeypatch.setattr(fake_ytdl, "extract_info", record_extract)
    downloader = _make_downloader(output_dir=tmp_path)

    downloader.download_video(url="https://www.youtube.com/watch?v=abc")

    assert extracted == [("https://www.youtube.com/watch?v=abc", False)]


def test_download_video_names_the_file_after_the_safe_title(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL], monkeypatch: pytest.MonkeyPatch
) -> None:
    downloaded: list[dict[str, Any]] = []

    def record_download(self: _FakeYoutubeDL, ie_result: dict[str, Any], download: bool = True) -> None:
        downloaded.append(ie_result)

    monkeypatch.setattr(fake_ytdl, "process_ie_result", record_download)
    fake_ytdl.info = {"title": "Song: Part/1?"}
    downloader = _make_downloader(output_dir=tmp_path)

    downloader.download_video(url="https://www.youtube.com/watch?v=abc")

    assert downloaded[0]["title"] == "Song Part1"


def test_download_video_saves_into_the_output_folder(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL]
) -> None:
    fake_ytdl.info = {"title": "x"}
    downloader = _make_downloader(output_dir=tmp_path)

    downloader.download_video(url="https://www.youtube.com/watch?v=abc")

    assert downloader.ydl_opts["outtmpl"] == "%(title)s.%(ext)s"
    assert downloader.ydl_opts["paths"] == {"home": str(tmp_path)}


def test_download_video_logs_when_no_info_is_returned(
    tmp_path: Path,
    fake_ytdl: type[_FakeYoutubeDL],
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    downloaded: list[dict[str, Any]] = []

    def record_download(self: _FakeYoutubeDL, ie_result: dict[str, Any], download: bool = True) -> None:
        downloaded.append(ie_result)

    monkeypatch.setattr(fake_ytdl, "process_ie_result", record_download)
    fake_ytdl.info = None
    downloader = _make_downloader(output_dir=tmp_path)

    with caplog.at_level(logging.ERROR, logger="score_snatcher.youtube_downloader"):
        downloader.download_video(url="https://www.youtube.com/watch?v=abc")

    assert downloaded == []
    assert "Failed to extract video information" in caplog.text


def test_download_video_logs_failures(
    tmp_path: Path,
    fake_ytdl: type[_FakeYoutubeDL],
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def failing_download(self: _FakeYoutubeDL, ie_result: dict[str, Any], download: bool = True) -> None:
        raise RuntimeError("disk full")

    monkeypatch.setattr(fake_ytdl, "process_ie_result", failing_download)
    fake_ytdl.info = {"title": "x"}
    downloader = _make_downloader(output_dir=tmp_path)

    with caplog.at_level(logging.ERROR, logger="score_snatcher.youtube_downloader"):
        downloader.download_video(url="https://www.youtube.com/watch?v=abc")

    assert "disk full" in caplog.text


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


def test_download_all_videos_processes_each_entry_with_a_url(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL], caplog: pytest.LogCaptureFixture
) -> None:
    downloader = _make_downloader(output_dir=tmp_path)

    fake_ytdl.info = {
        "entries": [
            {"url": "abc", "title": "First: Song?"},
            {"url": "https://www.youtube.com/watch?v=def", "title": "Second"},
            {"title": "No url"},
            {"url": "ghi"},
        ]
    }

    with caplog.at_level(logging.INFO, logger="score_snatcher.youtube_downloader"):
        downloader.download_all_videos_from_channel(channel_name="@handle")

    assert "Downloading video: First Song" in caplog.text
    assert "Downloading video: Second" in caplog.text
    assert "Downloading video: UnknownTitle" in caplog.text
    assert "Downloading video: No url" not in caplog.text


def test_download_all_videos_logs_when_channel_info_is_missing(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL], caplog: pytest.LogCaptureFixture
) -> None:
    downloader = _make_downloader(output_dir=tmp_path)
    fake_ytdl.info = None

    with caplog.at_level(logging.ERROR, logger="score_snatcher.youtube_downloader"):
        downloader.download_all_videos_from_channel(channel_name="@handle")

    assert "Could not fetch channel info" in caplog.text


def test_download_all_videos_logs_when_channel_has_no_entries(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL], caplog: pytest.LogCaptureFixture
) -> None:
    downloader = _make_downloader(output_dir=tmp_path)
    fake_ytdl.info = {"entries": []}

    with caplog.at_level(logging.ERROR, logger="score_snatcher.youtube_downloader"):
        downloader.download_all_videos_from_channel(channel_name="@handle")

    assert "No videos found" in caplog.text


def test_download_all_videos_logs_errors_from_yt_dlp(
    tmp_path: Path, fake_ytdl: type[_FakeYoutubeDL], caplog: pytest.LogCaptureFixture
) -> None:
    downloader = _make_downloader(output_dir=tmp_path)
    fake_ytdl.info = {"raise": True}

    with caplog.at_level(logging.ERROR, logger="score_snatcher.youtube_downloader"):
        downloader.download_all_videos_from_channel(channel_name="@handle")

    assert "Error while listing channel videos" in caplog.text
