import os
import json
import sqlite3
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import xml.etree.ElementTree as ET


class LightroomClassicTagger:
    def __init__(self, catalog_path=None):
        """Initialize the tagger with CLIP model and Lightroom catalog connection"""
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.catalog_path = catalog_path
        self.keywords = self.extract_keywords("./Foundation List 2.0.1.txt")

        # Pre-compute text features for efficiency
        self.text_features = None

    def extract_keywords(self, file_path):
        """
        Extract all keywords and their aliases from the Foundation List file.
        Returns a flat list of all terms.

        Args:
            file_path (str): Path to the Foundation List file

        Returns:
            list: List of all keywords and their aliases
        """
        keywords = set()

        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                # Skip empty lines, category headers, and indentation markers
                if not line or line.startswith("[") or line.isspace():
                    continue

                # Handle lines with aliases
                if "{" in line:
                    # Get main term
                    main_term = line.split("{")[0].strip()
                    keywords.add(main_term)

                    # Get aliases
                    aliases = [alias.strip("} ") for alias in line.split("{")[1:]]
                    keywords.update(aliases)
                else:
                    # Add regular terms
                    keywords.add(line)

        # Convert to sorted list and remove any empty strings
        return sorted([k for k in keywords if k])

    def connect_to_catalog(self):
        """Connect to Lightroom catalog SQLite database"""
        if not self.catalog_path or not os.path.exists(self.catalog_path):
            raise ValueError("Invalid Lightroom catalog path")
        return sqlite3.connect(self.catalog_path)

    def get_catalog_images(self):
        """Get list of images from Lightroom catalog"""
        conn = self.connect_to_catalog()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                f.id_local as file_id,
                rf.absolutePath || af.pathFromRoot || f.baseName || '.' || f.extension as full_path
            FROM AgLibraryFile f
            JOIN AgLibraryFolder af ON f.folder = af.id_local
            JOIN AgLibraryRootFolder rf ON af.rootFolder = rf.id_local
            WHERE f.extension IN ('NEF', 'JPG', 'JPEG', 'DNG', 'CR2', 'ARW')
        """)

        images = cursor.fetchall()
        conn.close()
        return images

    def generate_image_embeddings(self, image_path):
        """Generate CLIP embeddings for an image"""
        try:
            image = Image.open(image_path)
            if image.mode == "RGBA":
                image = image.convert("RGB")

            max_size = 1024
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                image = image.resize(new_size, Image.Resampling.LANCZOS)

            inputs = self.processor(images=image, return_tensors="pt", padding=True)
            image_features = self.model.get_image_features(**inputs)

            # Normalize the features
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            return image_features

        except Exception as e:
            print(f"Error processing image {image_path}: {str(e)}")
            return None

    def generate_text_embeddings(self):
        """Generate CLIP embeddings for all keywords"""
        if self.text_features is None:
            inputs = self.processor(
                text=self.keywords, return_tensors="pt", padding=True
            )
            self.text_features = self.model.get_text_features(**inputs)
            # Normalize the features
            self.text_features = self.text_features / self.text_features.norm(
                dim=-1, keepdim=True
            )
        return self.text_features

    def get_top_keywords(self, image_path, threshold=0.5, max_keywords=20):
        """Get top matching keywords for an image"""
        image_features = self.generate_image_embeddings(image_path)
        if image_features is None:
            return []

        text_features = self.generate_text_embeddings()

        try:
            # Calculate cosine similarity
            similarity = torch.matmul(image_features, text_features.T).squeeze()

            # Get top matches above threshold
            top_matches = []
            scores = similarity.tolist()

            for score, keyword in zip(scores, self.keywords):
                if score > threshold:
                    top_matches.append((keyword, float(score)))

            # Sort by score and limit to max_keywords
            top_matches.sort(key=lambda x: x[1], reverse=True)
            return top_matches[:max_keywords]

        except Exception as e:
            print(f"Error calculating similarities for {image_path}: {str(e)}")
            return []

    def update_xmp_sidecar(self, image_path, keywords):
        """Update or create XMP sidecar file with keywords"""
        xmp_path = os.path.splitext(image_path)[0] + ".xmp"

        ET.register_namespace("", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        ET.register_namespace("x", "adobe:ns:meta/")
        ET.register_namespace("dc", "http://purl.org/dc/elements/1.1/")

        if not os.path.exists(xmp_path):
            root = ET.Element("{adobe:ns:meta/}xmpmeta")
            rdf = ET.SubElement(
                root, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF"
            )
            description = ET.SubElement(
                rdf, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description"
            )
            subject = ET.SubElement(
                description, "{http://purl.org/dc/elements/1.1/}subject"
            )
            bag = ET.SubElement(
                subject, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Bag"
            )
        else:
            try:
                tree = ET.parse(xmp_path)
                root = tree.getroot()
                bag = root.find(".//{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Bag")
                if bag is None:
                    rdf = root.find(
                        ".//{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF"
                    )
                    if rdf is None:
                        rdf = ET.SubElement(
                            root, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF"
                        )
                    description = ET.SubElement(
                        rdf, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description"
                    )
                    subject = ET.SubElement(
                        description, "{http://purl.org/dc/elements/1.1/}subject"
                    )
                    bag = ET.SubElement(
                        subject, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Bag"
                    )
            except ET.ParseError:
                # If the file exists but is invalid XML, create new structure
                root = ET.Element("{adobe:ns:meta/}xmpmeta")
                rdf = ET.SubElement(
                    root, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF"
                )
                description = ET.SubElement(
                    rdf, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description"
                )
                subject = ET.SubElement(
                    description, "{http://purl.org/dc/elements/1.1/}subject"
                )
                bag = ET.SubElement(
                    subject, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Bag"
                )

        # Get existing keywords
        existing_keywords = set()
        for item in bag.findall("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li"):
            if item.text:
                existing_keywords.add(item.text.strip())

        # Add new keywords while preserving existing ones
        new_keywords = set(keyword for keyword, _ in keywords)
        all_keywords = existing_keywords.union(new_keywords)

        # Clear bag and add all keywords
        for item in bag.findall("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li"):
            bag.remove(item)

        for keyword in sorted(all_keywords):
            li = ET.SubElement(bag, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li")
            li.text = keyword

        # Print summary of changes
        new_added = new_keywords - existing_keywords
        if new_added:
            print(f"Added {len(new_added)} new keywords: {', '.join(new_added)}")
        print(f"Total keywords: {len(all_keywords)}")

        # Write to file
        tree = ET.ElementTree(root)
        tree.write(xmp_path, encoding="UTF-8", xml_declaration=True)

    def process_catalog(self, output_path=None):
        """Process all images in the Lightroom catalog"""
        if not self.catalog_path:
            raise ValueError("Catalog path not set")

        results = {}
        images = self.get_catalog_images()
        total_images = len(images)

        for idx, (image_id, image_path) in enumerate(images, 1):
            print(f"Processing image {idx}/{total_images}: {image_path}")
            try:
                keywords = self.get_top_keywords(image_path)
                if keywords:
                    results[image_path] = keywords
                    self.update_xmp_sidecar(image_path, keywords)
                    print(f"Found {len(keywords)} keywords")
                else:
                    print("No keywords found")

            except Exception as e:
                print(f"Error processing {image_path}: {str(e)}")

        # Save results to JSON if output_path provided
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

        return results


def main():
    # Example usage
    catalog_path = r"E:\Lightroom\Catalog/2024.lrcat"
    tagger = LightroomClassicTagger(catalog_path)

    # Process entire catalog
    results = tagger.process_catalog("keyword_suggestions.json")


if __name__ == "__main__":
    main()
