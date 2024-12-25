# LightroomClassicTagger API Reference

## Class: LightroomClassicTagger

Main class for handling image analysis and keyword generation.

### Constructor

```python
LightroomClassicTagger(catalog_path=None, image_folder=None, keywords_file="src/lr_autotag/Foundation List 2.0.1.txt")
```

#### Parameters:
- `catalog_path` (str, optional): Path to Lightroom catalog file
- `image_folder` (str, optional): Path to folder containing images
- `keywords_file` (str): Path to keywords hierarchy file

### Methods

#### process_catalog()
```python
def process_catalog(output_path=None, overwrite=False, dry_run=False)
```
Process all images in the catalog or folder.

#### get_top_keywords()
```python
def get_top_keywords(image_path, threshold=0.25, max_keywords=20)
```
Generate keywords for a single image.

#### update_xmp_sidecar()
```python
def update_xmp_sidecar(image_path, keywords, overwrite=False)
```
Update or create XMP sidecar file with keywords.

### Example Usage

```python
# Initialize tagger
tagger = LightroomClassicTagger(catalog_path="path/to/catalog.lrcat")

# Process entire catalog
tagger.process_catalog(output_path="results.json")

# Process single image
keywords = tagger.get_top_keywords("path/to/image.jpg")
```
