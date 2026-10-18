"""Tests for the constants module."""

from score_snatcher import constants


# Testing the paths defined in the constants module.


def test_project_root_contains_the_pyproject_file() -> None:
    assert (constants.PROJECT_ROOT / "pyproject.toml").is_file()


def test_config_paths_point_into_the_package() -> None:
    assert constants.CONFIG_PATH.is_file()
    assert constants.SONG_CONFIG_PATH.is_file()
