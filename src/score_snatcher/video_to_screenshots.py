"""Module for managing the screenshot folders of the video workflow."""

from pathlib import Path


class VideoToScreenshots:
    """Manage the screenshot folder for one video.

    Attributes:
        root_dir_path (Path): Folder that holds the screenshot folders.
        output_dir_name (str): Name of the screenshot folder for this video.

    Example:
        >>> screenshots = VideoToScreenshots(root_dir_path=Path("data/screenshots"),
        ...                                  output_dir_name="my_video")
        >>> screenshots.extract_screenshots_from_video()
    """

    def __init__(self, root_dir_path: Path, output_dir_name: str) -> None:
        """Store where the screenshots of the video go.

        Args:
            root_dir_path (Path): Folder that holds the screenshot folders.
            output_dir_name (str): Name of the screenshot folder for this video.
        """

        self.root_dir_path = root_dir_path
        self.output_dir_name = output_dir_name

    def _check_if_already_processed(self) -> bool:
        """Check whether the screenshot folder exists and is empty.

        Returns:
            is_empty_folder (bool): True if the folder exists and has no entries.
        """

        folder_path = self.root_dir_path / self.output_dir_name

        if not folder_path.exists():
            return False

        entries = folder_path.iterdir()
        has_entries = any(entries)

        return not has_entries

    def extract_screenshots_from_video(self) -> None:
        """Extract the screenshots from the video.

        Work in progress: not implemented yet.
        """

        # if self._check_if_already_processed():
        #     return
