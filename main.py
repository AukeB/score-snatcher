"""Main module to execute program functionalities."""

import logging

from src.youtube_to_pdf import YoutubeToPDF

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def main() -> None:
    """Main execution function."""

    url = "https://www.youtube.com/watch?v=MciqL-IJY5I"
    
    video_to_pdf = YoutubeToPDF(url=url)
    video_to_pdf.execute()


if __name__ == "__main__":
    main()