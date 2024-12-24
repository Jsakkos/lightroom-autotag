import click
from .tagger import LightroomClassicTagger

@click.command()
@click.option("--catalog", help="Path to Lightroom catalog")
@click.option("--image-folder", help="Path to folder containing images")
@click.option("--output", default="keyword_suggestions.json", help="Output JSON file")
@click.option("--threshold", default=0.5, help="Confidence threshold for keywords")
@click.option("--max-keywords", default=20, help="Maximum keywords per image")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keywords")
@click.option("--keywords-file", default="src/lr_autotag/Foundation List 2.0.1.txt", help="Path to the keywords file")
def main(catalog, image_folder, output, threshold, max_keywords, overwrite, keywords_file):
    """AI-powered keyword tagging for Adobe Lightroom Classic"""
    tagger = LightroomClassicTagger(catalog, image_folder, keywords_file)
    tagger.process_catalog(output, overwrite)

if __name__ == "__main__":
    main()
