"""Module for downloading videos from YouTube using yt-dlp."""

from yt_dlp import YoutubeDL
from pathlib import Path
import logging

from src.score_snatcher.constants import YT_DLP_DOWNLOAD_FORMAT


logger = logging.getLogger(__name__)


class YoutubeDownloader:
    """Class containing functions for downloading videos from YouTube."""

    def __init__(self, output_dir_path: Path, url: str) -> None:
        """Initialize the YoutubeDownloader with a URL and output settings."""
        self.output_dir_path = output_dir_path
        self.url = url
        self.output_file_extension = "mp4"

        self.video_title = self._get_video_title()

    def _get_video_title(self) -> str:
        """Return the title of a YouTube video without downloading it."""
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
        }

        with YoutubeDL(ydl_opts) as ydl:  # type: ignore
            info: dict = ydl.extract_info(self.url, download=False)  # type: ignore
            return info["title"]  # type: ignore

    def _check_if_video_already_downloaded(self, output_file_name: str) -> bool:
        """Check if the video file already exists in the output directory."""
        output_path: Path = self.output_dir_path / f"{output_file_name}.mp4"

        if output_path.exists():
            logger.info(f'⏩ Video already downloaded: "{output_path.name}"')
            return True

        return False

    def _download_using_yt_dlp(
        self,
        output_file_name: str,
    ) -> None:
        """Download the video from YouTube using yt-dlp."""
        ydl_opts = {
            "outtmpl": str(self.output_dir_path / f"{output_file_name}.%(ext)s"),
            "format": YT_DLP_DOWNLOAD_FORMAT,
            "merge_output_format": self.output_file_extension,
            "quiet": True,
        }

        try:
            with YoutubeDL(ydl_opts) as youtube_dl:  # type: ignore
                youtube_dl.download([self.url])

            logger.info(
                f'✅ Download finished for video: "{self.video_title}" ({self.url})'
            )
            logger.info(
                f"✅ Video saved to: {self.output_dir_path / (output_file_name + '.mp4')}"
            )
        except Exception as e:
            logger.error(f"❌ Download failed for {self.url}: {e}")

    def download_videos(
        self,
        output_file_name: str,
    ) -> None:
        """Wrapper function to trigger the YouTube video download."""
        if not self._check_if_video_already_downloaded(
            output_file_name=output_file_name
        ):
            logger.info(
                f'✅ Starting download for video: "{self.video_title}" ({self.url})'
            )

            self._download_using_yt_dlp(output_file_name=output_file_name)
