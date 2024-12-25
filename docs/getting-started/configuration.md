# Configuration Guide

Learn how to configure Lightroom AI Tagger for optimal performance and results.

## Configuration Options

### Command Line Options

These settings can be configured per run:

| Option          | Description              | Default                   | Example                      |
| --------------- | ------------------------ | ------------------------- | ---------------------------- |
| `threshold`     | Minimum confidence score | 0.5                       | `--threshold 0.3`            |
| `max-keywords`  | Keywords per image       | 20                        | `--max-keywords 30`          |
| `keywords-file` | Custom keywords list     | Foundation List 2.0.1.txt | `--keywords-file custom.txt` |


## Keywords File Format

The keywords file should follow this format:

```
[Category Name]
keyword1
keyword2 {alias1, alias2}
  subcategory1
  subcategory2 {alt1, alt2}
```

Example:
```
[Nature]
landscape
mountain {mountains, mountainous}
  alpine
  rocky {rocks, rocky terrain}
```

## Performance Tuning

### GPU Acceleration

Enable GPU support by:
1. Installing CUDA drivers
2. Setting environment variables:
```bash
export CUDA_VISIBLE_DEVICES=0
```

### Memory Usage

Control memory usage with:
- Batch size adjustments
- Image size limits
- Process count settings

## Example Configurations

### Low Accuracy Mode
```bash
lr-autotag --catalog "photos.lrcat" \
    --threshold 0.25 \
    --max-keywords 30
```

### Fast Processing Mode
```bash
lr-autotag --catalog "photos.lrcat" \
    --threshold 0.5 \
    --max-keywords 15
```

### Custom Keywords Mode
```bash
lr-autotag --catalog "photos.lrcat" \
    --keywords-file "custom_keywords.txt" \
    --threshold 0.4
```
