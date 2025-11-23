"""Module for downloading videos from YouTube using yt-dlp."""

import logging

from yt_dlp import YoutubeDL
from pathlib import Path

from src.score_snatcher.config_manager import ConfigManager


logger = logging.getLogger(__name__)


class YoutubeDownloader:
    """Class containing functions for downloading videos from YouTube."""

    def __init__(self, output_dir_path: Path, url: str) -> None:
        """
        Initialize the YoutubeDownloader with a URL and output directory.

        Args:
            output_dir_path (Path): Path to the directory where the video will be saved.
            url (str): The URL of the YouTube video to download.
        """
        self.output_dir_path = output_dir_path
        self.url = url

        # Load Youtube download settings from the config file.
        config_manager = ConfigManager()
        config = config_manager.load_config_file()
        self.config_youtube_download = config.youtube_downloader

        self.ydl_opts: dict = self._construct_ydl_opts_dict()
        self.video_title = self._obtain_video_title()

    def _construct_ydl_opts_dict(self) -> dict:
        """
        Construct the dictionary of options for yt-dlp based on the configuration.

        Returns:
            dict: yt-dlp options dictionary.
        """
        cfg = self.config_youtube_download

        ydl_opts = {
            "format": cfg.video_quality,
            "ignoreerrors": cfg.ignore_errors,
            "no_warnings": cfg.no_warnings,
            "extract_flat": cfg.extract_flat,
            "writesubtitles": cfg.write_subtitles,
            "writethumbnail": cfg.write_thumbnail,
            "writeautomaticsub": cfg.write_automatic_sub,
            "postprocessors": [
                {
                    "key": cfg.post_processors_key,
                    "preferedformat": cfg.output_file_extension,
                }
            ],
            "keepvideo": cfg.keep_video,
            "clean_infojson": cfg.clean_info_json,
            "retries": cfg.retries,
            "fragment_retries": cfg.fragment_retries,
            "noplaylist": cfg.no_playlist,
        }

        return ydl_opts

    def _obtain_video_title(self) -> str | None:
        """
        Extract the title of the video without downloading it.

        Returns:
            str: The video title, or 'Unknown' if extraction fails.
        """
        try:
            with YoutubeDL(self.ydl_opts) as ydl:  # type: ignore
                info = ydl.extract_info(url=self.url, download=False)

                if info is None:
                    logger.error(
                        f"Failed to extract video information for URL: {self.url}. "
                        "Video may be private or unavailable."
                    )

                    return "Unknown"

                video_title = info.get("title", "Unknown")

                return video_title

        except Exception as e:
            logger.error(f"Error extracting video title for URL {self.url}: {e}")
            return "Unknown"

    def download_video(self, output_file_name: str) -> None:
        """
        Download the YouTube video to the specified output directory.

        Args:
            output_file_name (str): Name of the output file (without path).
        """
        output_file_path = self.output_dir_path / output_file_name
        self.ydl_opts["outtmpl"] = str(output_file_path) + ".%(ext)s"

        logger.info(f"Starting download: {self.url}")
        logger.info(f"Saving to: {output_file_path}")

        try:
            with YoutubeDL(self.ydl_opts) as ydl:  # type: ignore
                ydl.download([self.url])

            logger.info(f"Download completed: {output_file_path}")

        except Exception as e:
            logger.error(f"Failed to download video {self.url}: {e}")

    def download_all_videos_from_channel(self, channel_name: str) -> None:
        """
        Download all videos from a YouTube channel using the existing download_video method.

        Args:
            channel_name (str): Channel handle or channel URL.
        """
        if channel_name.startswith("@"):
            channel_url = f"https://www.youtube.com/{channel_name}"
        elif channel_name.startswith("UC"):  # raw channel ID
            channel_url = f"https://www.youtube.com/channel/{channel_name}"
        elif channel_name.startswith("http"):
            channel_url = channel_name
        else:
            channel_url = f"https://www.youtube.com/c/{channel_name}"

        logger.info(f"Fetching video list for channel: {channel_url}")

        # # yt-dlp options for listing videos without downloading
        # list_opts = {
        #     "quiet": True,
        #     "extract_flat": True,    # Important — faster, gives list of uploads
        #     "skip_download": True,
        #     "ignoreerrors": True,
        #     "no_warnings": True,
        #     "playlistend": 99999,    # Ensure we get all videos
        # }

        # try:
        #     with YoutubeDL(list_opts) as ydl: # type: ignore
        #         info = ydl.extract_info(channel_url, download=False)

        #     if info is None:
        #         logger.error(f"Could not fetch channel info: {channel_url}")
        #         return

        #     # Info for channels or playlist-like objects is stored in "entries"
        #     entries = info.get("entries", [])

        #     if not entries:
        #         logger.error(f"No videos found for channel: {channel_url}")
        #         return

        #     logger.info(f"Found {len(entries)} videos on channel.")

        #     # Iterate through each entry and download individually
        #     for entry in entries:
        #         video_url = entry.get("url")

        #         if not video_url:
        #             logger.warning("Encountered entry without a URL; skipping.")
        #             continue

        #         full_video_url = (
        #             video_url if video_url.startswith("http")
        #             else f"https://www.youtube.com/watch?v={video_url}"
        #         )

        #         video_title = entry.get("title", "UnknownTitle")
        #         safe_title = "".join(
        #             c for c in video_title if c.isalnum() or c in " _-.()"
        #         ).strip()

        #         logger.info(f"Downloading video: {safe_title}")

        #         # Use your existing method
        #         output_name = safe_title
        #         self.url = full_video_url     # Update instance URL
        #         self.video_title = safe_title # Helpful for logging
        #         self.download_video(output_name)

        #     logger.info(f"All videos from channel '{channel_name}' downloaded successfully.")

        # except Exception as e:
        #     logger.error(f"Error while downloading channel videos: {e}")
