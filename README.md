# Lightroom AI Tagger

An intelligent tagging assistant for Adobe Lightroom Classic that uses OpenAI's CLIP model to automatically generate relevant keywords for your photos.

## Features

- Automatically analyze images in your Lightroom catalog using CLIP neural network
- Generate relevant keywords based on image content
- Update XMP sidecar files with AI-generated keywords while preserving existing ones
- Configurable confidence threshold and maximum keywords per image
- Supports common RAW formats (NEF, CR2, ARW) and JPEGs
- Uses the Foundation List 2.0.1 keyword hierarchy for consistent tagging

## Requirements

- Python 3.8+
- Adobe Lightroom Classic
- PyTorch
- transformers
- Pillow
- sqlite3

## Installation

You can install `lr-autotag` directly from PyPI:

```bash
pip install lr-autotag
```

Or, for development:

1. Clone this repository:
```bash
git clone https://github.com/yourusername/lr-autotag.git
cd lr-autotag
```

2. Install with UV in development mode:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

3. Download the Foundation List file and place it in the project directory.

## Usage

1. Close Lightroom Classic if it's running

2. Modify the catalog path in the script to point to your Lightroom catalog:
```python
catalog_path = "path/to/your/catalog.lrcat"
```

3. Run the script:
```bash
python lightroom-tagger.py
```

The script will:
- Scan your Lightroom catalog for images
- Generate AI keywords for each image
- Create or update XMP sidecar files with the new keywords
- Save a JSON report of all suggestions

### Important Notes
- Always ensure you have enough disk space for catalog backups
- Backup files are not automatically cleaned up - you may want to periodically remove old backups
- The backup process might take a few moments for large catalogs

## Configuration

You can adjust these parameters in the script:

- `threshold`: Confidence threshold for keyword suggestions (default: 0.5)
- `max_keywords`: Maximum number of keywords per image (default: 20)
- `max_size`: Maximum image dimension for processing (default: 1024)

## How It Works

1. The script connects to your Lightroom catalog's SQLite database to get image locations
2. Each image is processed through the CLIP neural network
3. The image embeddings are compared against pre-computed embeddings of the Foundation List keywords
4. Keywords with similarity scores above the threshold are selected
5. The keywords are written to XMP sidecar files that Lightroom can read

## Safety Features

### Catalog Backup
Before any operations that access the Lightroom catalog, the tool automatically creates a timestamped backup of your catalog file. The backup is stored in the same directory as your original catalog with the format: `[original_name]_YYYYMMDD_HHMMSS.backup`.

If the backup process fails for any reason, the tool will not proceed with catalog operations to ensure your data's safety.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI's CLIP model
- The Digital Photography School Foundation List[https://lightroom-keyword-list-project.blogspot.com/]
- Adobe Lightroom Classic SDK documentation

## Disclaimer

This tool is not affiliated with or endorsed by Adobe. Use at your own risk and always backup your Lightroom catalog before using any third-party tools.