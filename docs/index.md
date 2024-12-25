# Lightroom AI Tagger Documentation

Welcome to the documentation for Lightroom AI Tagger, an intelligent tagging assistant for Adobe Lightroom Classic that leverages OpenAI's CLIP model to automatically generate relevant keywords for your photos.

## Overview

Lightroom AI Tagger helps photographers streamline their workflow by:

- Automatically analyzing images using advanced AI
- Generating relevant keywords based on image content
- Updating XMP sidecar files while preserving existing keywords
- Supporting RAW and JPEG formats
- Using industry-standard keyword hierarchies

## Quick Start

1. Install the package:
```bash
pip install lr-autotag
```

2. Run the tagger:
```bash
lr-autotag --catalog "path/to/catalog.lrcat"
```

Or for a folder of images:
```bash
lr-autotag --image-folder "path/to/images"
```

## Safety Features

- Automatic catalog backups
- Non-destructive keyword updates
- Dry-run mode for testing

## Next Steps

- Read the [Installation Guide](getting-started/installation.md) for detailed setup instructions
- Check the [Basic Usage](getting-started/basic-usage.md) guide to get started
