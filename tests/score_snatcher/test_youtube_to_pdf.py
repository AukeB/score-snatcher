"""Tests for the youtube_to_pdf module."""

from pathlib import Path
from typing import Any

import pytest

from score_snatcher import youtube_to_pdf as module
from score_snatcher.youtube_to_pdf import YoutubeToPDF


class _FakeDownloader:
    """Stand-in for YoutubeDownloader, with a fixed title and no network access.

    Attributes:
        channel_calls (list[str]): Channels that were asked to be listed.
    """

    title = "Aint Misbehaving: Live!"

    def __init__(self) -> None:
        """Start without any recorded calls."""

        self.channel_calls: list[str] = []

    def obtain_video_title(self, url: str) -> str:
        """Return the fixed title, as the real downloader would for this URL.

        Args:
            url (str): The video URL. Unused.

        Returns:
            video_title (str): The fixed title.
        """

        return _FakeDownloader.title

    def download_all_videos_from_channel(self, channel_name: str) -> None:
        """Record the channel that would be listed.

        Args:
            channel_name (str): The channel to list.
        """

        self.channel_calls.append(channel_name)


@pytest.fixture(name="workflow")
def fixture_workflow(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> YoutubeToPDF:
    """Provide a workflow whose data folders and downloader are fake.

    Args:
        tmp_path (Path): Pytest's per-test temporary folder.
        monkeypatch (pytest.MonkeyPatch): Pytest's patching helper.

    Returns:
        workflow (YoutubeToPDF): The workflow, with data folders under tmp_path.
    """

    monkeypatch.setattr(module, "OUTPUT_DIR_VIDEOS", tmp_path / "data" / "videos")
    monkeypatch.setattr(module, "OUTPUT_DIR_SCREENSHOTS", tmp_path / "data" / "screenshots")
    monkeypatch.setattr(module, "OUTPUT_DIR_PDFS", tmp_path / "data" / "pdfs")
    monkeypatch.setattr(module, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(module, "YoutubeDownloader", _FakeDownloader)

    workflow = YoutubeToPDF(url="https://www.youtube.com/watch?v=abc")

    return workflow


# Testing the "__init__" method from the "YoutubeToPDF" class.


def test_init_creates_the_data_folders(workflow: YoutubeToPDF, tmp_path: Path) -> None:
    assert (tmp_path / "data" / "videos").is_dir()
    assert (tmp_path / "data" / "screenshots").is_dir()
    assert (tmp_path / "data" / "pdfs").is_dir()


def test_init_logs_when_it_creates_the_data_folders(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setattr(module, "OUTPUT_DIR_VIDEOS", tmp_path / "new" / "videos")
    monkeypatch.setattr(module, "OUTPUT_DIR_SCREENSHOTS", tmp_path / "new" / "shots")
    monkeypatch.setattr(module, "OUTPUT_DIR_PDFS", tmp_path / "new" / "pdfs")
    monkeypatch.setattr(module, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(module, "YoutubeDownloader", _FakeDownloader)
    caplog.set_level("INFO")

    YoutubeToPDF(url="https://www.youtube.com/watch?v=abc")

    assert "Data folders created" in caplog.text


def test_init_does_not_log_when_the_data_folders_already_exist(
    workflow: YoutubeToPDF,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level("INFO")

    YoutubeToPDF(url="https://www.youtube.com/watch?v=abc")

    assert "Data folders created" not in caplog.text


def test_init_formats_the_video_title(workflow: YoutubeToPDF) -> None:
    assert workflow.formatted_video_name == "aint_misbehaving_live"


# Testing the "_format_video_name" method from the "YoutubeToPDF" class.


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("Café Déjà Vu", "cafe_deja_vu"),
        ("  --Hello...World--  ", "hello_world"),
        ("Song (Part 2) [HD]", "song_part_2_hd"),
        ("", ""),
    ],
)
def test_format_video_name_makes_titles_file_safe(title: str, expected: str) -> None:
    assert YoutubeToPDF._format_video_name(video_name=title) == expected


def test_format_video_name_truncates_long_titles() -> None:
    title = "a" * 99 + "_" + "b" * 20

    formatted = YoutubeToPDF._format_video_name(video_name=title, max_length=100)

    assert len(formatted) == 99
    assert not formatted.endswith("_")


# Testing the "execute" method from the "YoutubeToPDF" class.


def test_execute_lists_the_channel(workflow: YoutubeToPDF) -> None:
    workflow.execute()

    downloader: Any = workflow.youtube_downloader
    assert downloader.channel_calls == ["https://www.youtube.com/c/JérémyFloury"]
