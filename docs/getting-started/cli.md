# Command Line Interface

The `lr-autotag` command line interface provides several options for controlling the tagging process.

## Basic Usage

```bash
lr-autotag --catalog "path/to/catalog.lrcat"
# or
lr-autotag --image-folder "path/to/images"
```

## Available Options

| Option            | Short | Description                              | Default                   |
| ----------------- | ----- | ---------------------------------------- | ------------------------- |
| `--catalog`       | `-c`  | Path to Lightroom catalog file           | None                      |
| `--image-folder`  | `-i`  | Path to folder containing images         | None                      |
| `--output`        | `-o`  | Output JSON file for keyword suggestions | keyword_suggestions.json  |
| `--threshold`     | `-t`  | Confidence threshold for keywords        | 0.5                       |
| `--max-keywords`  | `-m`  | Maximum keywords per image               | 20                        |
| `--overwrite`     |       | Overwrite existing keywords              | False                     |
| `--dry-run`       |       | Don't modify XMP files                   | False                     |
| `--keywords-file` |       | Path to custom keywords file             | Foundation List 2.0.1.txt |

## Examples

Process a Lightroom catalog with custom settings:
```bash
lr-autotag --catalog "photos.lrcat" --threshold 0.3 --max-keywords 30
```

Process a folder of images in dry-run mode:
```bash
lr-autotag --image-folder "vacation_photos" --dry-run --output "keywords.json"
```

Use a custom keywords list:
```bash
lr-autotag --catalog "photos.lrcat" --keywords-file "my_keywords.txt"
```

## Exit Codes

| Code | Meaning                            |
| ---- | ---------------------------------- |
| 0    | Success                            |
| 1    | Invalid arguments or configuration |
| 2    | Processing error                   |

## Environment Variables

- `CUDA_VISIBLE_DEVICES`: Control GPU usage
- `LR_AUTOTAG_DEBUG`: Enable debug logging when set to "1"
