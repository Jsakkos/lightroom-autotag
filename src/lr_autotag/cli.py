import click
from .tagger import LightroomClassicTagger


@click.command()
@click.option("--catalog", required=True, help="Path to Lightroom catalog")
@click.option("--output", default="keyword_suggestions.json", help="Output JSON file")
@click.option("--threshold", default=0.5, help="Confidence threshold for keywords")
@click.option("--max-keywords", default=20, help="Maximum keywords per image")
def main(catalog, output, threshold, max_keywords):
    """AI-powered keyword tagging for Adobe Lightroom Classic"""
    tagger = LightroomClassicTagger(catalog)
    tagger.process_catalog(output)


if __name__ == "__main__":
    main()
