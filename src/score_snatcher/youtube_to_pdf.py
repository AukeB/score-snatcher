"""Module for the score-snatcher workflow, from a YouTube video to a PDF score."""

import logging
import re
import unicodedata
from pathlib import Path

from score_snatcher.constants import (
    OUTPUT_DIR_PDFS_REL_PATH,
    OUTPUT_DIR_SCREENSHOTS_REL_PATH,
    OUTPUT_DIR_VIDEOS_REL_PATH,
    PROJECT_ROOT,
)
from score_snatcher.youtube_downloader import YoutubeDownloader

logger = logging.getLogger(__name__)


class YoutubeToPDF:
    """Run the score-snatcher workflow for one YouTube video.

    Attributes:
        url (str): The URL of the video.
        videos_dir (Path): Folder for the downloaded videos.
        screenshots_dir (Path): Folder for the extracted screenshots.
        pdfs_dir (Path): Folder for the generated PDFs.
        youtube_downloader (YoutubeDownloader): Downloads the video and reads its title.
        formatted_video_name (str): The video title, made safe for file names.

    Example:
        >>> video_to_pdf = YoutubeToPDF(url="https://www.youtube.com/watch?v=...")
        >>> video_to_pdf.execute()
    """

    def __init__(self, url: str) -> None:
        """Create the data folders and read the title of the video.

        Args:
            url (str): The URL of the video.
        """

        self.url = url

        self.videos_dir = PROJECT_ROOT / OUTPUT_DIR_VIDEOS_REL_PATH
        self.screenshots_dir = PROJECT_ROOT / OUTPUT_DIR_SCREENSHOTS_REL_PATH
        self.pdfs_dir = PROJECT_ROOT / OUTPUT_DIR_PDFS_REL_PATH

        self.directories = [self.videos_dir, self.screenshots_dir, self.pdfs_dir]
        self._create_data_folders()

        self.youtube_downloader = YoutubeDownloader(
            output_dir_path=self.videos_dir,
            url=self.url,
        )

        self.formatted_video_name = self._format_video_name(
            video_name=self.youtube_downloader.video_title,
        )

    @staticmethod
    def _format_video_name(video_name: str, max_length: int = 100) -> str:
        """Make a video title safe for file names.

        Normalizes to ASCII, lowercases, collapses separators into single underscores,
        removes other punctuation, and truncates to max_length.

        Args:
            video_name (str): The video title.
            max_length (int): The longest allowed name, in characters.

        Returns:
            formatted_name (str): The file-name-safe version of the title.
        """

        normalized = unicodedata.normalize("NFKD", video_name)
        ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
        lowercase_name = ascii_name.lower()
        underscored = re.sub(r"[ \t\n._-]+", "_", lowercase_name)
        without_symbols = re.sub(r"[^\w]", "", underscored)
        formatted_name = without_symbols.strip("_")

        if len(formatted_name) > max_length:
            formatted_name = formatted_name[:max_length].rstrip("_")

        return formatted_name

    def _create_data_folders(self) -> None:
        """Create the data folders, if they do not exist yet."""

        for directory in self.directories:
            directory.mkdir(parents=True, exist_ok=True)

        data_root = PROJECT_ROOT / "data"
        logger.info(f"✅ Data folders created at: {data_root}")

    def execute(self) -> None:
        """Run the workflow.

        Work in progress: only the download of the channel's video list runs. The
        download, screenshot and PDF steps are still commented out below.
        """

        # Step 1. Download the youtube video.
        # self.youtube_downloader.download_video(
        #     output_file_name=self.formatted_video_name
        # )
        self.youtube_downloader.download_all_videos_from_channel(
            channel_name="https://www.youtube.com/c/JérémyFloury",
        )

        # Step 2. Extract screenshots from video every x amount of seconds.
        # video_to_screenshots = VideoToScreenshots(
        #     root_dir_path=self.screenshots_dir,
        #     output_dir_name=self.formatted_video_name,
        # )
        # video_to_screenshots.extract_screenshots_from_video()

        # Step 3. Remove duplicate screenshots.
        # to implement

        # Step 4. Merge screenshots in PDF document.
        # to implement.
