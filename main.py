"""Entry point for score-snatcher."""

import logging

from score_snatcher.youtube_to_pdf import YoutubeToPDF

_URLS = [
    "https://www.youtube.com/watch?v=MciqL-IJY5I",
    "https://www.youtube.com/watch?v=baDIFo45vE8&list=RDbaDIFo45vE8",
]


def main() -> None:
    """Run the workflow for each video URL."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # for song in song_config:
    for url in _URLS:
        # url = song.url
        video_to_pdf = YoutubeToPDF(url=url)
        video_to_pdf.execute()


if __name__ == "__main__":
    main()
