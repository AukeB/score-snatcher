# Score Snatcher

Repository for turning YouTube videos of musical scores into good looking PDF documents.

## Status

Work in progress. The workflow is set up, and the channel's video list is read from YouTube. The
download, screenshot and PDF steps are still commented out in `YoutubeToPDF.execute` and
`VideoToScreenshots`.

## Running

```bash
uv sync
uv run python main.py
```

Download settings live in `src/score_snatcher/configs/config.yaml`. Song entries live in the CSV
files in the same folder. Downloads and other output go into `data/` at the project root.

## Development

```bash
uv run pytest      # tests, with 100% line and branch coverage of src/
uv run ruff check .
```

The tests never touch the network: yt-dlp is replaced by a fake.
