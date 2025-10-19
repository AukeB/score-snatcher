"""Module for downloading videos from YouTube using yt-dlp."""

from yt_dlp import YoutubeDL
from pathlib import Path
import logging


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
            info = ydl.extract_info(self.url, download=False)
            return info["title"]  # type: ignore

    def _download_using_yt_dlp(
        self,
        output_file_name: str,
    ) -> None:
        """Download the video from YouTube using yt-dlp."""
        ydl_opts = {
            "outtmpl": str(self.output_dir_path / f"{output_file_name}.%(ext)s"),
            "format": "bestvideo[ext=mp4]/bestvideo",
            "merge_output_format": self.output_file_extension,
            "quiet": True,
        }

        try:
            with YoutubeDL(ydl_opts) as youtube_dl:  # type: ignore
                youtube_dl.download([self.url])
            logging.info(f"✅ Download finished for: {self.url}")
        except Exception as e:
            logging.error(f"❌ Download failed for {self.url}: {e}")

    def download_videos(
        self,
        output_file_name: str,
    ) -> None:
        """Wrapper function to trigger the YouTube video download."""
        logging.info(f'Starting download for "{self.video_title}" ({self.url}))')

        self._download_using_yt_dlp(output_file_name=output_file_name)
