# Basic Usage Guide

This guide covers the fundamental workflow for using Lightroom AI Tagger.

## Workflow Overview

1. Prepare your images in Lightroom Classic
2. Close Lightroom Classic
3. Run the tagger
4. Review and import the keywords in Lightroom

## Step-by-Step Instructions

### 1. Prepare Your Images

- Ensure your images are properly imported into Lightroom Classic
- Organize images into collections if desired
- Make sure all images have XMP sidecar files enabled:
  - Go to Catalog Settings > Metadata
  - Check "Automatically write changes into XMP"

### 2. Run the Tagger

Basic command for processing a Lightroom catalog:

```bash
lr-autotag --catalog "path/to/catalog.lrcat"
```

Or process a folder of images:

```bash
lr-autotag --image-folder "path/to/images"
```

### 3. Review Results

The tool will:
- Process each image through the AI model
- Generate relevant keywords
- Update XMP sidecar files
- Create a JSON report (optional)

Example output:
```
Processing image 1/50: DSC_0001.NEF
Found 15 keywords
Added new keywords: landscape, mountain, sunset, nature
Total keywords: 15

Processing image 2/50: DSC_0002.NEF
Found 12 keywords
Added new keywords: portrait, indoor, lighting
Total keywords: 12
```

### 4. Import Keywords in Lightroom

1. Reopen Lightroom Classic
2. Select the processed images
3. From the menu: Metadata > Read Metadata from Files
4. Review the imported keywords in the Keywording panel

## Tips for Best Results

- Use the `--threshold` option to adjust keyword sensitivity
- Start with `--dry-run` to preview changes
- Use `--max-keywords` to limit the number of keywords per image
- Keep Lightroom closed while processing to avoid conflicts

## Common Workflows

### Batch Processing New Images

```bash
lr-autotag --image-folder "new_photos" --threshold 0.3 --max-keywords 25
```

### Testing Settings

```bash
lr-autotag --catalog "catalog.lrcat" --dry-run --output "test_results.json"
```

### Overwriting Existing Keywords

```bash
lr-autotag --catalog "catalog.lrcat" --overwrite
```
