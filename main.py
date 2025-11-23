"""Main module to execute program functionalities."""

import logging

from src.score_snatcher.config_manager import ConfigManager
from src.score_snatcher.youtube_to_pdf import YoutubeToPDF

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main() -> None:
    """Main execution function."""

    config_manager = ConfigManager()
    song_config = config_manager.load_song_csv()

    urls = [
        "https://www.youtube.com/watch?v=MciqL-IJY5I",
        "https://www.youtube.com/watch?v=baDIFo45vE8&list=RDbaDIFo45vE8"
    ]

    #for song in song_config:
    for url in urls:
        # url = song.url
        video_to_pdf = YoutubeToPDF(url=url)
        video_to_pdf.execute()


if __name__ == "__main__":
    main()