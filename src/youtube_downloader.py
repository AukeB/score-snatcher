"""Module for downloading videos from YouTube using yt-dlp."""

from yt_dlp import YoutubeDL
from pathlib import Path
import logging


class YoutubeDownloader:
    """Class containing functions for downloading videos from YouTube."""

    def __init__(self, url: str) -> None:
        """Initialize the YoutubeDownloader with a URL and output settings."""
        self.url = url
        self.output_dir_path = Path(__file__).resolve().parent.parent / "data/videos"
        self.output_file_extension = "mp4"

        logging.info(f"Initialized downloader for URL: {self.url}")

    def download_using_yt_dlp(self) -> None:
        """Download the video from YouTube using yt-dlp."""
        ydl_opts = {
            "outtmpl": str(self.output_dir_path / "%(title)s.%(ext)s"),
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

    def download_videos(self) -> None:
        """Wrapper function to trigger the YouTube video download."""
        logging.info(f"Starting download for {self.url}")
        self.download_using_yt_dlp()
