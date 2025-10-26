""" """

import re
import logging
import unicodedata

from pathlib import Path

from src.score_snatcher.constants import (
    OUTPUT_DIR_VIDEOS_REL_PATH,
    OUTPUT_DIR_SCREENSHOTS_REL_PATH,
    OUTPUT_DIR_PDFS_REL_PATH,
)
from src.score_snatcher.youtube_downloader import YoutubeDownloader
from src.score_snatcher.video_to_screenshots import VideoToScreenshots


logger = logging.getLogger(__name__)


class YoutubeToPDF:
    """Central class to execute the entire project workflow."""

    def __init__(self, url: str) -> None:
        """Initialisation of the VideoToPDF class."""
        self.url = url
        self.repo_root = Path(__file__).resolve().parent.parent

        self.videos_dir = self.repo_root / OUTPUT_DIR_VIDEOS_REL_PATH
        self.screenshots_dir = self.repo_root / OUTPUT_DIR_SCREENSHOTS_REL_PATH
        self.pdfs_dir = self.repo_root / OUTPUT_DIR_PDFS_REL_PATH

        self.directories = [self.videos_dir, self.screenshots_dir, self.pdfs_dir]

        self._create_data_folders()

        # Already initialize YoutubeDownloader class here so we can obtain and
        # format the video name.
        self.youtube_downloader = YoutubeDownloader(
            output_dir_path=self.videos_dir,
            url=self.url,
        )

        self.formatted_video_name = self._format_video_name(
            video_name=self.youtube_downloader.video_title  # type: ignore
        )

    @staticmethod
    def _format_video_name(video_name: str, max_length: int = 100) -> str:
        """
        Format a YouTube video title to be safe for file systems.

        - Converts to lowercase
        - Normalizes unicode characters
        - Removes or replaces unsafe filesystem characters
        - Replacelogger = logging.getLogger(__name__)s spaces and consecutive spaces with single underscore
        - Truncates if longer than max_length
        - Strips leading and trailing underscores or dots
        """

        video_name = unicodedata.normalize("NFKD", video_name)
        video_name = video_name.encode("ascii", "ignore").decode("ascii")
        video_name = video_name.lower()
        video_name = re.sub(r"\s+", "_", video_name)
        video_name = re.sub(r"[^\w.-]", "", video_name)
        video_name = video_name.strip("_.-")

        if len(video_name) > max_length:
            video_name = video_name[:max_length].rstrip("_.-")

        return video_name

    def _create_data_folders(self) -> None:
        """Create all data folders if they don't exist."""

        for dir in self.directories:
            dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"✅ Data folders created at: {self.repo_root / 'data'}")

    def execute(self) -> None:
        """Run the full workflow."""

        # Step 1. Download the youtube video.
        self.youtube_downloader.download_videos(
            output_file_name=self.formatted_video_name
        )

        # Step 2. Extract screenshots from video every x amount of seconds.
        video_to_screenshots = VideoToScreenshots(
            root_dir_path=self.screenshots_dir,
            output_dir_name=self.formatted_video_name,
        )

        video_to_screenshots.extract_screenshots_from_video()

        # Step 3. Remove duplicate screenshots.
        # to implement

        # Step 4. Merge screenshots in PDF document.
        # to implement.
