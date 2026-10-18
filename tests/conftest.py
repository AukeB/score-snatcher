"""Shared pytest fixtures. Network access is never needed: yt-dlp is replaced by fakes."""

from pathlib import Path
from typing import Any

import pytest

from score_snatcher.config_manager import ConfigManager
from score_snatcher.config_model import ConfigModel

SONG_CSV_HEADER = "generate,song,composer,performer,transcriber,url"


@pytest.fixture(name="config")
def fixture_config() -> ConfigModel:
    """Provide the configuration shipped with the package.

    Returns:
        config (ConfigModel): The validated default configuration.
    """

    config = ConfigManager().load_config_file()

    return config


@pytest.fixture(name="song_csv")
def fixture_song_csv(tmp_path: Path) -> Path:
    """Provide a song CSV with one valid row, one invalid row and one skipped row.

    Args:
        tmp_path (Path): Pytest's per-test temporary folder.

    Returns:
        csv_path (Path): The CSV file.
    """

    csv_path = tmp_path / "songs.csv"

    rows = [
        SONG_CSV_HEADER,
        "TRUE,Aint Misbehaving,Fats Waller,Fats Waller,Jeremy,https://www.youtube.com/watch?v=abc",
        "MAYBE,Broken,Composer,Performer,Transcriber,https://www.youtube.com/watch?v=def",
        "FALSE,Skipped,Composer,Performer,Transcriber,https://www.youtube.com/watch?v=ghi",
    ]

    content = "\n".join(rows) + "\n"
    csv_path.write_text(content, encoding="utf-8")

    return csv_path


class _FakeYoutubeDL:
    """Stand-in for yt_dlp.YoutubeDL that returns canned information.

    Attributes:
        info (dict[str, Any] | None): The information returned by extract_info.
        options (dict[str, Any]): The options the instance was created with.
        downloaded (list[str]): The URLs passed to download.
    """

    info: dict[str, Any] | None = None

    def __init__(self, options: dict[str, Any]) -> None:
        """Remember the options the instance was created with.

        Args:
            options (dict[str, Any]): The yt-dlp options.
        """

        self.options = options
        self.downloaded: list[str] = []

    def __enter__(self) -> "_FakeYoutubeDL":
        """Return the instance for use in a with-block.

        Returns:
            self (_FakeYoutubeDL): This instance.
        """

        return self

    def __exit__(self, *exc_info: object) -> None:
        """Do nothing when the with-block ends."""

    def extract_info(self, url: str, download: bool = True) -> dict[str, Any] | None:
        """Return the canned information, or raise if none was set.

        Args:
            url (str): The URL to inspect. Unused.
            download (bool): Unused.

        Returns:
            info (dict[str, Any] | None): The canned information.
        """

        if _FakeYoutubeDL.info == {"raise": True}:
            raise RuntimeError("network down")

        return _FakeYoutubeDL.info

    def download(self, urls: list[str]) -> None:
        """Record the URLs that would have been downloaded.

        Args:
            urls (list[str]): The URLs to download.
        """

        self.downloaded.extend(urls)


@pytest.fixture(name="fake_ytdl")
def fixture_fake_ytdl(monkeypatch: pytest.MonkeyPatch) -> type[_FakeYoutubeDL]:
    """Replace yt-dlp's YoutubeDL in the downloader module with the fake.

    Args:
        monkeypatch (pytest.MonkeyPatch): Pytest's patching helper.

    Returns:
        fake (type[_FakeYoutubeDL]): The fake class, with its canned info reset to None.
    """

    import score_snatcher.youtube_downloader as downloader_module

    monkeypatch.setattr(downloader_module, "YoutubeDL", _FakeYoutubeDL)
    _FakeYoutubeDL.info = None

    return _FakeYoutubeDL
