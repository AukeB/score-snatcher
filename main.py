"""Main module to execute program functionalities."""

from pathlib import Path
import logging

from src.utils import create_output_directories
from src.youtube_downloader import YoutubeDownloader

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    """Main execution function."""
    
    # Create the directories required for the output of the program.
    create_output_directories()

    url = "https://www.youtube.com/watch?v=MciqL-IJY5I"

    youtube_downloader = YoutubeDownloader(url=url)
    youtube_downloader.download_videos()


if __name__ == "__main__":
    main()