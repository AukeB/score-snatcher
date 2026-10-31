"""Module for downloading videos from YouTube with yt-dlp."""

import logging
from pathlib import Path
from typing import Any

from yt_dlp import YoutubeDL

from score_snatcher.config_manager import ConfigManager
from score_snatcher.constants import OUTPUT_DIR_VIDEOS

logger = logging.getLogger(__name__)

_UNKNOWN_TITLE = "Unknown"


class YoutubeDownloader:
    """Download YouTube videos, and read their titles, with the settings from
    config.yaml.

    Attributes:
        output_dir_path (Path): Folder the videos are saved to.
        config_youtube_download (ConfigModel.YoutubeDownloaderConfig): The download
            settings.
        ydl_opts (dict[str, Any]): The options passed to yt-dlp.

    Example:
        Download one video:

        >>> downloader = YoutubeDownloader()
        >>> downloader.download_video(url="https://www.youtube.com/watch?v=abc")

        Download all videos from a channel:

        >>> downloader = YoutubeDownloader()
        >>> downloader.download_all_videos_from_channel(channel_name="@handle")
    """

    def __init__(self, output_dir_path: Path = OUTPUT_DIR_VIDEOS) -> None:
        """Load the download settings and create the output folder if needed.

        Args:
            output_dir_path (Path): Folder the videos are saved to. Created if it
                does not exist yet.
        """

        self.output_dir_path = output_dir_path
        self.output_dir_path.mkdir(parents=True, exist_ok=True)

        config = ConfigManager().load_config_file()
        self.config_youtube_download = config.youtube_downloader

        self.ydl_opts = self._construct_ydl_opts_dict()

    def _construct_ydl_opts_dict(self) -> dict[str, Any]:
        """Translate the download settings into yt-dlp options.

        Returns:
            ydl_opts (dict[str, Any]): The options for yt-dlp.
        """

        cfg = self.config_youtube_download

        postprocessor = {
            "key": cfg.post_processors_key,
            "preferedformat": cfg.output_file_extension,
        }

        ydl_opts: dict[str, Any] = {
            "format": cfg.video_quality,
            "ignoreerrors": cfg.ignore_errors,
            "no_warnings": cfg.no_warnings,
            "extract_flat": cfg.extract_flat,
            "writesubtitles": cfg.write_subtitles,
            "writethumbnail": cfg.write_thumbnail,
            "writeautomaticsub": cfg.write_automatic_sub,
            "postprocessors": [postprocessor],
            "keepvideo": cfg.keep_video,
            "clean_infojson": cfg.clean_info_json,
            "retries": cfg.retries,
            "fragment_retries": cfg.fragment_retries,
            "noplaylist": cfg.no_playlist,
        }

        return ydl_opts

    @staticmethod
    def _channel_name_to_url(channel_name: str) -> str:
        """Turn a channel handle, ID, URL or legacy name into a channel URL.

        Args:
            channel_name (str): The channel identifier to convert.

        Returns:
            channel_url (str): The URL of the channel.
        """

        if channel_name.startswith("@"):
            channel_url = f"https://www.youtube.com/{channel_name}"
        elif channel_name.startswith("UC"):
            channel_url = f"https://www.youtube.com/channel/{channel_name}"
        elif channel_name.startswith("http"):
            channel_url = channel_name
        else:
            channel_url = f"https://www.youtube.com/c/{channel_name}"

        return channel_url

    @staticmethod
    def _to_watch_url(video_url: str) -> str:
        """Turn a bare video ID into a watch URL, leaving full URLs unchanged.

        Args:
            video_url (str): A full URL or a bare video ID.

        Returns:
            watch_url (str): The full watch URL.
        """

        if video_url.startswith("http"):
            watch_url = video_url
        else:
            watch_url = f"https://www.youtube.com/watch?v={video_url}"

        return watch_url

    @staticmethod
    def _make_safe_title(video_title: str) -> str:
        """Keep only letters, digits and a few punctuation marks from a title.

        Args:
            video_title (str): The raw video title.

        Returns:
            safe_title (str): The title without characters that are unsafe in file
                names.
        """

        kept_characters = [c for c in video_title if c.isalnum() or c in " _-.()"]
        safe_title = "".join(kept_characters).strip()

        return safe_title

    @staticmethod
    def _read_title(info: dict[str, Any]) -> str:
        """Read the title from the information yt-dlp returned for a video.

        Args:
            info (dict[str, Any]): The video information.

        Returns:
            video_title (str): The title, or "Unknown" if it is missing or not text.
        """

        raw_title = info.get("title")
        video_title = raw_title if isinstance(raw_title, str) else _UNKNOWN_TITLE

        return video_title

    def obtain_video_title(self, url: str) -> str:
        """Read the title of a video without downloading it.

        Args:
            url (str): The URL of the video.

        Returns:
            video_title (str): The title, or "Unknown" if it cannot be read.
        """

        try:
            with YoutubeDL(self.ydl_opts) as ydl:  # pyright: ignore[reportArgumentType]
                info = ydl.extract_info(url=url, download=False)

            if info is None:
                logger.error(
                    f"Failed to extract video information for URL: {url}. "
                     "Video may be private or unavailable."
                )

                return _UNKNOWN_TITLE

            video_title = self._read_title(info=info)

            return video_title

        except Exception as error:
            logger.error(f"Error extracting video title for URL {url}: {error}")

            return _UNKNOWN_TITLE

    def download_video(self, url: str) -> None:
        """Download the video into the output folder, named after its title.

        The video information is read once and the download uses that same
        information, so YouTube is only asked for it once.

        Args:
            url (str): The URL of the video.
        """

        self.ydl_opts["outtmpl"] = "%(title)s.%(ext)s"
        self.ydl_opts["paths"] = {"home": str(self.output_dir_path)}

        logger.info(f"Starting download: {url}")

        try:
            with YoutubeDL(self.ydl_opts) as ydl:  # pyright: ignore[reportArgumentType]
                info = ydl.extract_info(url=url, download=False)

                if info is None:
                    logger.error(
                        f"Failed to extract video information for URL: {url}. "
                        "Video may be private or unavailable."
                    )

                    return

                video_title = self._read_title(info=info)
                info["title"] = self._make_safe_title(video_title=video_title)

                ydl.process_ie_result(info, download=True)

            logger.info(f"Download completed: {url}")

        except Exception as error:
            logger.error(f"Failed to download video {url}: {error}")

    def download_all_videos_from_channel(self, channel_name: str) -> None:
        """List a channel's videos and process each one.

        Work in progress: the per-video download call is still commented out, so no
        video is downloaded yet.

        Args:
            channel_name (str): Channel handle, channel ID, URL, or legacy channel name.
        """

        channel_url = self._channel_name_to_url(channel_name=channel_name)

        logger.info(f"Fetching video list for channel: {channel_url}")

        list_opts: dict[str, Any] = {
            "quiet": True,
            "extract_flat": True,
            "skip_download": True,
            "ignoreerrors": True,
            "no_warnings": True,
            "playlistend": 99999,
        }

        try:
            with YoutubeDL(list_opts) as ydl:  # pyright: ignore[reportArgumentType]
                info = ydl.extract_info(channel_url, download=False)

            if info is None:
                logger.error(f"Could not fetch channel info: {channel_url}")

                return

            raw_entries: Any = info.get("entries", [])
            entries: list[Any] = list(raw_entries)

            if not entries:
                logger.error(f"No videos found for channel: {channel_url}")

                return

            entry_count = len(entries)
            logger.info(f"Found {entry_count} videos on channel.")

            for entry in entries:
                video_url = entry.get("url")

                if not video_url:
                    logger.warning("Encountered entry without a URL; skipping.")
                    continue

                full_video_url = self._to_watch_url(video_url=video_url)
                raw_title = entry.get("title")
                video_title = (
                    raw_title if isinstance(raw_title, str) else "UnknownTitle"
                )
                safe_title = self._make_safe_title(video_title=video_title)

                logger.info(f"Downloading video: {safe_title}")
                logger.debug(f"Video title: {video_title}")
                logger.debug(f"Video URL: {full_video_url}")

                # self.download_video(url=full_video_url)

            logger.info(f"All videos from channel '{channel_name}' processed.")

        except Exception as error:
            logger.error(f"Error while listing channel videos: {error}")
