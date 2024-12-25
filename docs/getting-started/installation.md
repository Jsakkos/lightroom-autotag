# Installation Guide

## System Requirements

- Python 3.9 or higher
- Adobe Lightroom Classic
- 4GB+ RAM recommended
- CUDA-capable GPU (optional, for faster processing)

## Installation Methods

### Using pip (Recommended)

```bash
pip install lr-autotag
```

### Development Installation

1. Clone the repository:
```bash
git clone https://github.com/jsakkos/lr-autotag.git
cd lr-autotag
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e ".[dev]"
```

## Verifying Installation

Test your installation:

```bash
lr-autotag --help
```

You should see the following output:

```
Usage: lr-autotag [OPTIONS]

  AI-powered keyword tagging for Adobe Lightroom Classic

Options:
  --catalog TEXT         Path to Lightroom catalog
  --image-folder TEXT    Path to folder containing images
  --output TEXT         Output JSON file  [default: keyword_suggestions.json]
  --threshold FLOAT     Confidence threshold for keywords  [default: 0.5]
  --max-keywords INTEGER  Maximum keywords per image  [default: 20]
  --overwrite          Overwrite existing keywords
  --dry-run           Don't modify XMP files, only save suggestions
  --keywords-file TEXT  Path to the keywords file
  --help              Show this message and exit.
```

## Troubleshooting

### Common Issues

1. CUDA/GPU errors:
   - Ensure you have compatible NVIDIA drivers
   - Try running with CPU only

2. Import errors:
   - Verify Python version compatibility
   - Check for missing dependencies
