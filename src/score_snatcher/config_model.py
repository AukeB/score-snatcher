"""Module for the configuration schemas of score-snatcher."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class ConfiguredBaseModel(BaseModel):
    """BaseModel that forbids extra arguments not explicitly defined."""

    model_config = ConfigDict(extra="forbid")


class SongEntry(ConfiguredBaseModel):
    """One row of the song CSV file.

    Attributes:
        generate (str): "TRUE" to process the song, "FALSE" to skip it.
        song (str): Title of the song.
        composer (str): Composer of the song.
        performer (str): Performer in the video.
        transcriber (str): Person who transcribed the score.
        url (str): YouTube URL of the video.
    """

    generate: Literal["TRUE", "FALSE"]
    song: str
    composer: str
    performer: str
    transcriber: str
    url: str


class ConfigModel(ConfiguredBaseModel):
    """Main configuration model combining all project parameters.

    Attributes:
        youtube_downloader (ConfigModel.YoutubeDownloaderConfig): Download settings.
    """

    class YoutubeDownloaderConfig(ConfiguredBaseModel):
        """Settings for the YouTube downloader, passed on to yt-dlp.

        Attributes:
            output_file_extension (str): Extension of the downloaded video.
            video_quality (str): yt-dlp format selector, such as
                "bestvideo[height<=1080]".
            ignore_errors (bool): Skip videos that fail instead of stopping.
            no_warnings (bool): Suppress warning messages.
            extract_flat (bool): Only list URLs instead of full video information.
            write_subtitles (bool): Download subtitles.
            write_thumbnail (bool): Save the video thumbnail.
            write_automatic_sub (bool): Download automatic subtitles.
            post_processors_key (str): Post-processor to run, such as FFmpeg conversion.
            keep_video (bool): Keep intermediate files after merging.
            clean_info_json (bool): Delete the generated .info.json files.
            retries (int): Retries after a network or download error.
            fragment_retries (int): Retries for each fragment of a DASH stream.
            no_playlist (bool): Never download a playlist, even if the URL is one.
        """

        output_file_extension: str
        video_quality: str
        ignore_errors: bool
        no_warnings: bool
        extract_flat: bool
        write_subtitles: bool
        write_thumbnail: bool
        write_automatic_sub: bool
        post_processors_key: str
        keep_video: bool
        clean_info_json: bool
        retries: int
        fragment_retries: int
        no_playlist: bool

    youtube_downloader: YoutubeDownloaderConfig
