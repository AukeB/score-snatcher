"""Tests for the video_to_screenshots module."""

from pathlib import Path

from score_snatcher.video_to_screenshots import VideoToScreenshots


# Testing the "_check_if_already_processed" method from the "VideoToScreenshots" class.


def test_check_if_already_processed_is_false_when_folder_is_missing(tmp_path: Path) -> None:
    screenshots = VideoToScreenshots(root_dir_path=tmp_path, output_dir_name="video")

    assert screenshots._check_if_already_processed() is False


def test_check_if_already_processed_is_true_for_an_empty_folder(tmp_path: Path) -> None:
    (tmp_path / "video").mkdir()
    screenshots = VideoToScreenshots(root_dir_path=tmp_path, output_dir_name="video")

    assert screenshots._check_if_already_processed() is True


def test_check_if_already_processed_is_false_when_folder_has_files(tmp_path: Path) -> None:
    (tmp_path / "video").mkdir()
    (tmp_path / "video" / "frame.png").write_bytes(b"")
    screenshots = VideoToScreenshots(root_dir_path=tmp_path, output_dir_name="video")

    assert screenshots._check_if_already_processed() is False


# Testing the "extract_screenshots_from_video" method from the "VideoToScreenshots" class.


def test_extract_screenshots_from_video_does_nothing_yet(tmp_path: Path) -> None:
    screenshots = VideoToScreenshots(root_dir_path=tmp_path, output_dir_name="video")

    screenshots.extract_screenshots_from_video()

    remaining = tmp_path.iterdir()

    assert list(remaining) == []
