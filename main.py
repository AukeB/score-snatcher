"""Main module to execute program functionalities."""

import logging

from src.video_to_pdf import VideoToPDF

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    """Main execution function."""

    url = "https://www.youtube.com/watch?v=MciqL-IJY5I"
    
    video_to_pdf = VideoToPDF(url=url)
    video_to_pdf.execute()


if __name__ == "__main__":
    main()