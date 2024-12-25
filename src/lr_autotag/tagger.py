import os
import json
import sqlite3
import torch
import shutil
from datetime import datetime
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import xml.etree.ElementTree as ET

BACKUP_EXTENSION = '.backup'

class LightroomClassicTagger:
    def __init__(self, catalog_path=None, image_folder=None, keywords_file="src/lr_autotag/Foundation List 2.0.1.txt"):
        """Initialize the tagger with CLIP model and Lightroom catalog connection"""
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.catalog_path = catalog_path
        self.image_folder = image_folder
        self.keywords_file = keywords_file
        self.keywords = self.extract_keywords(keywords_file)

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
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Keywords file not found: {file_path}")

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
        print(f"Loaded {len(keywords)} keywords from {file_path}")
        # Convert to sorted list and remove any empty strings
        return sorted([k for k in keywords if k])

    def backup_catalog(self):
        """Create a backup of the Lightroom catalog before processing"""
        if not self.catalog_path or not os.path.exists(self.catalog_path):
            raise ValueError("Invalid Lightroom catalog path")

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{self.catalog_path}_{timestamp}{BACKUP_EXTENSION}"
        
        try:
            shutil.copy2(self.catalog_path, backup_path)
            print(f"Created catalog backup: {backup_path}")
            return True
        except Exception as e:
            print(f"Failed to create catalog backup: {str(e)}")
            return False

    def connect_to_catalog(self):
        """Connect to Lightroom catalog SQLite database with backup"""
        if not self.catalog_path or not os.path.exists(self.catalog_path):
            raise ValueError("Invalid Lightroom catalog path")
        
        # Create backup before connecting
        if not self.backup_catalog():
            raise RuntimeError("Failed to create catalog backup, aborting connection")
            
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

    def get_folder_images(self):
        """Get list of images from the specified folder"""
        if not self.image_folder or not os.path.exists(self.image_folder):
            raise ValueError("Invalid image folder path")
        
        supported_extensions = ('.nef', '.jpg', '.jpeg', '.dng', '.cr2', '.arw', '.png', '.tif', '.tiff')
        images = [
            os.path.join(root, file)
            for root, _, files in os.walk(self.image_folder)
            for file in files
            if file.lower().endswith(supported_extensions)
        ]
        return [(None, image) for image in images]

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
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)

            # Normalize the features
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            # Move to CPU if on GPU
            return image_features.cpu()

        except Exception as e:
            print(f"Error processing image {image_path}: {str(e)}")
            return None

    def generate_text_embeddings(self):
        """Generate CLIP embeddings for all keywords"""
        if self.text_features is None:
            print(f"Generating embeddings for {len(self.keywords)} keywords...")
            inputs = self.processor(
                text=self.keywords, return_tensors="pt", padding=True
            )
            with torch.no_grad():
                self.text_features = self.model.get_text_features(**inputs)
            # Normalize the features
            self.text_features = self.text_features / self.text_features.norm(
                dim=-1, keepdim=True
            )
            # Move to CPU
            self.text_features = self.text_features.cpu()
            print("Text embeddings generated successfully")
        return self.text_features

    def get_top_keywords(self, image_path, threshold=0.25, max_keywords=20):  # Lowered threshold
        """Get top matching keywords for an image"""
        image_features = self.generate_image_embeddings(image_path)
        if image_features is None:
            return []

        text_features = self.generate_text_embeddings()

        try:
            # Ensure both tensors are on CPU and calculate cosine similarity
            similarity = torch.matmul(image_features, text_features.T).squeeze()
            
            # Get top matches above threshold
            top_matches = []
            scores = similarity.numpy().tolist()  # Convert to numpy then to list

            for score, keyword in zip(scores, self.keywords):
                if score > threshold:
                    top_matches.append((keyword, float(score)))
                    
            # Sort by score and limit to max_keywords
            top_matches.sort(key=lambda x: x[1], reverse=True)
            if not top_matches:
                print(f"No keywords found above threshold {threshold}")
            return top_matches[:max_keywords]

        except Exception as e:
            print(f"Error calculating similarities for {image_path}: {str(e)}")
            return []

    def update_xmp_sidecar(self, image_path, keywords, overwrite=False):
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
        if overwrite:
            # Clear all existing keywords
            for item in bag.findall("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li"):
                bag.remove(item)
            all_keywords = set(keyword for keyword, _ in keywords)
            new_keywords = all_keywords
        else:

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

    def process_catalog(self, output_path=None, overwrite=False, dry_run=False):
        """Process all images in the Lightroom catalog or specified folder"""
        if not self.catalog_path and not self.image_folder:
            raise ValueError("Either catalog path or image folder must be set")

        results = {}
        images = self.get_catalog_images() if self.catalog_path else self.get_folder_images()
        total_images = len(images)

        if dry_run:
            print("DRY RUN: No XMP files will be modified")

        for idx, (image_id, image_path) in enumerate(images, 1):
            print(f"Processing image {idx}/{total_images}: {image_path}")
            try:
                keywords = self.get_top_keywords(image_path)
                if keywords:
                    results[image_path] = keywords
                    if not dry_run:
                        self.update_xmp_sidecar(image_path, keywords, overwrite)
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
    pass

if __name__ == "__main__":
    main()
