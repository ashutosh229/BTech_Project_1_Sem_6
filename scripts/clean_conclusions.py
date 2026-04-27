import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class ConclusionCleaner:
    """
    Cleans extracted conclusion text by removing artifacts, metadata,
    and normalizing whitespace.
    """

    def __init__(self, input_file: str, output_file: str = None):
        """
        Initialize the cleaner.

        Args:
            input_file: Path to the conclusions_data.json file to clean
            output_file: Path to save cleaned conclusions (defaults to cleaned_conclusions_data.json)
        """
        self.input_file = input_file
        self.output_file = output_file or input_file.replace(".json", "_cleaned.json")
        self.cleaned_data = None
        self.stats = {
            "total_cases": 0,
            "cleaned_cases": 0,
            "total_chars_removed": 0,
        }

    def clean_text(self, text: str) -> str:
        """
        Clean conclusion text by removing artifacts, normalizing whitespace,
        and removing metadata.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        if not text:
            return text

        original_length = len(text)

        # Remove page indicators (Page X of Y)
        text = re.sub(r"Page\s+\d+\s+of\s+\d+", "", text)

        # Remove NEUTRAL CITATION headers and metadata
        text = re.sub(r"NEUTRAL CITATION\s*\n*", "", text)
        text = re.sub(r"C/SCA/\d+\s*", "", text)
        text = re.sub(r"CAV JUDGMENT DATED:.*?(?=\n|$)", "", text)
        text = re.sub(r"undefined\s*", "", text)

        # Remove signature blocks (Sd/-, judge names)
        text = re.sub(r"Sd/-\s*\n*", "", text)
        text = re.sub(r"\(.*?[A-Z]\.\s+[A-Z]\..*?[A-Z].*?,.*?[A-Z].*?\)", "", text)

        # Remove case numbers at end (Case No. X of XXXX)
        text = re.sub(r"Case\s+No\.\s+\d+\s+of\s+\d+", "", text)

        # Remove location and date metadata at end
        text = re.sub(r"New Delhi\s+Date:\s*\d+\.\d+\.\d+", "", text)
        text = re.sub(r"CHANDRESH", "", text)

        # Remove section headers that leaked into conclusions
        text = re.sub(r"Court\'s Reasoning|Precedent Analysis", "", text)

        # Normalize whitespace: multiple spaces to single space
        text = re.sub(r" +", " ", text)

        # Normalize newlines: excessive newlines to max 2 (paragraph break)
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
        text = re.sub(r"\n\s+\n", "\n\n", text)

        # Remove leading/trailing whitespace from each line
        lines = text.split("\n")
        lines = [line.strip() for line in lines]
        text = "\n".join(lines)

        # Remove excessive leading/trailing whitespace
        text = text.strip()

        # Clean up any remaining multiple spaces
        text = re.sub(r" {2,}", " ", text)

        # Track characters removed
        cleaned_length = len(text)
        self.stats["total_chars_removed"] += original_length - cleaned_length

        return text

    def load_conclusions(self) -> None:
        """Load conclusions from input JSON file."""
        print(f"\n📂 Loading conclusions from: {self.input_file}")

        with open(self.input_file, "r", encoding="utf-8") as f:
            self.cleaned_data = json.load(f)

        print(f"✓ Loaded {len(self.cleaned_data.get('conclusions', []))} cases")

    def clean_all_conclusions(self) -> None:
        """Clean all conclusions in the loaded data."""
        if not self.cleaned_data:
            print("⚠️  No data loaded. Run load_conclusions() first.")
            return

        conclusions_list = self.cleaned_data.get("conclusions", [])
        self.stats["total_cases"] = len(conclusions_list)

        print(f"\n🧹 Cleaning {len(conclusions_list)} conclusions...")
        print("=" * 70)

        for idx, case in enumerate(conclusions_list, 1):
            if case.get("conclusion"):
                original_conclusion = case["conclusion"]
                cleaned_conclusion = self.clean_text(original_conclusion)

                # Update the conclusion with cleaned version
                case["conclusion"] = cleaned_conclusion
                self.stats["cleaned_cases"] += 1

                # Also clean conclusion paragraphs if they exist
                if "conclusion_paragraphs" in case:
                    for para in case["conclusion_paragraphs"]:
                        if "text" in para:
                            para["text"] = self.clean_text(para["text"])

                status = "✓"
            else:
                status = "⚠️ (no conclusion)"

            print(
                f"[{idx}/{len(conclusions_list)}] {case.get('case_id', 'Unknown')}: {status}"
            )

        print("=" * 70)

    def save_cleaned_conclusions(self) -> str:
        """
        Save cleaned conclusions to output JSON file.

        Returns:
            Path to saved file
        """
        if not self.cleaned_data:
            print("⚠️  No data to save. Run clean_all_conclusions() first.")
            return None

        # Update metadata
        self.cleaned_data["metadata"]["cleaning_date"] = datetime.now().isoformat()
        self.cleaned_data["metadata"]["cleaning_stats"] = self.stats

        output_dir = os.path.dirname(self.output_file)
        os.makedirs(output_dir, exist_ok=True)

        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(self.cleaned_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Cleaned conclusions saved to: {self.output_file}")
        print(f"   File size: {os.path.getsize(self.output_file) / 1024:.2f} KB")

        return self.output_file

    def print_statistics(self) -> None:
        """Print cleaning statistics."""
        print("\n" + "=" * 70)
        print("📊 CLEANING STATISTICS")
        print("=" * 70)
        print(f"Total cases processed: {self.stats['total_cases']}")
        print(f"Cases cleaned: {self.stats['cleaned_cases']}")
        print(f"Total characters removed: {self.stats['total_chars_removed']:,} chars")
        print("=" * 70 + "\n")

    def run_full_pipeline(self) -> str:
        """
        Execute the complete cleaning pipeline.

        Returns:
            Path to cleaned output file
        """
        self.load_conclusions()
        self.clean_all_conclusions()
        output_path = self.save_cleaned_conclusions()
        self.print_statistics()
        return output_path


def main():
    """Main execution function."""

    # Configuration
    INPUT_FILE = "data/conclusions_data.json"
    OUTPUT_FILE = "data/conclusions_data_cleaned.json"

    # Create cleaner instance and run pipeline
    cleaner = ConclusionCleaner(input_file=INPUT_FILE, output_file=OUTPUT_FILE)
    cleaner.run_full_pipeline()


if __name__ == "__main__":
    main()
