"""Module for managing screenshot directories in a video processing workflow."""

from pathlib import Path


class VideoToScreenshots:
    """Class to manage screenshot directories for a video processing workflow."""

    def __init__(
        self,
        root_dir_path: Path,
        output_dir_name: str,
    ) -> None:
        """
        Initialize the VideoToScreenshots object.

        Args:
            root_dir_path (Path): Path to the root directory where the output
                folder should be located.
            output_dir_name (str): Name of the folder to store screenshots.
        """
        self.root_dir_path = root_dir_path
        self.output_dir_name = output_dir_name

    def _check_if_already_processed(self) -> bool:
        """
        Check if the screenshots folder exists and is empty.

        Returns:
            True if the folder exists and is empty, False otherwise.
        """
        folder_path: Path = self.root_dir_path / self.output_dir_name
        return folder_path.exists() and not any(folder_path.iterdir())

    def extract_screenshots_from_video(self) -> None:  # -> Optional[bool]:
        """ """
        pass

        # if self._check_if_already_processed():
        #     return False
