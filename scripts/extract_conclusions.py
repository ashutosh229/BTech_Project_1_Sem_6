import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class ConclusionExtractor:
    """
    Extracts conclusion and reasoning sections from case judgment JSON files
    and consolidates them into a single conclusions database.
    """

    def __init__(self, input_dir: str, output_dir: str = None):
        """
        Initialize the extractor.

        Args:
            input_dir: Directory containing JSON case files
            output_dir: Directory to save conclusions (defaults to input_dir)
        """
        self.input_dir = input_dir
        self.output_dir = output_dir or input_dir
        self.conclusions_data = []
        self.processed_files = 0
        self.failed_files = 0
        self.error_log = []

    def clean_text(self, text: str) -> str:
        """
        Clean extracted section text (conclusion or reasoning) by removing artifacts,
        normalizing whitespace, and removing metadata.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text
        """
        import re
        
        if not text:
            return text
        
        # Remove page indicators (Page X of Y)
        text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text)
        
        # Remove NEUTRAL CITATION headers and metadata
        text = re.sub(r'NEUTRAL CITATION\s*\n*', '', text)
        text = re.sub(r'C/SCA/\d+\s*', '', text)
        text = re.sub(r'CAV JUDGMENT DATED:.*?(?=\n|$)', '', text)
        text = re.sub(r'undefined\s*', '', text)
        
        # Remove signature blocks (Sd/-, judge names)
        text = re.sub(r'Sd/-\s*\n*', '', text)
        text = re.sub(r'\(.*?[A-Z]\.\s+[A-Z]\..*?[A-Z].*?,.*?[A-Z].*?\)', '', text)
        
        # Remove case numbers at end (Case No. X of XXXX)
        text = re.sub(r'Case\s+No\.\s+\d+\s+of\s+\d+', '', text)
        
        # Remove location and date metadata at end
        text = re.sub(r'New Delhi\s+Date:\s*\d+\.\d+\.\d+', '', text)
        text = re.sub(r'CHANDRESH', '', text)
        
        # Remove section headers that may have leaked into the text
        text = re.sub(r'Court\'s Reasoning|Precedent Analysis|Conclusion', '', text)
        
        # Normalize whitespace: multiple spaces to single space
        text = re.sub(r' +', ' ', text)
        
        # Normalize newlines: excessive newlines to max 2 (paragraph break)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r'\n\s+\n', '\n\n', text)
        
        # Remove leading/trailing whitespace from each line
        lines = text.split('\n')
        lines = [line.strip() for line in lines]
        text = '\n'.join(lines)
        
        # Remove excessive leading/trailing whitespace
        text = text.strip()
        
        # Remove "undefined" text fragments
        text = re.sub(r'undefined', '', text)
        
        # Clean up any remaining multiple spaces
        text = re.sub(r' {2,}', ' ', text)
        
        return text

    def extract_conclusion_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract conclusion from a single JSON case file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Dictionary with case_id, case_title, url, and conclusion data
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                case_data = json.load(f)

            # Extract basic case information
            case_info = {
                "case_id": (
                    case_data.get("url", "").split("/")[-2]
                    if case_data.get("url")
                    else None
                ),
                "case_title": case_data.get("case_title", "Unknown"),
                "url": case_data.get("url", ""),
                "court_name": case_data.get("court_name", ""),
                "page_title": case_data.get("page_title", ""),
                "conclusion": None,
                "conclusion_paragraphs": [],
                "reasoning": None,
                "reasoning_paragraphs": [],
            }

            def extract_id_number(item):
                item_id = item.get("id", "p_0")
                try:
                    numeric_part = int(item_id.split("_")[-1])
                    return numeric_part
                except (ValueError, IndexError):
                    return 0

            def extract_section(title):
                paragraphs = []
                # Try from elements_by_title
                if "elements_by_title" in case_data and title in case_data["elements_by_title"]:
                    paragraphs = case_data["elements_by_title"][title]
                # If not found, check all_paragraphs
                elif "all_paragraphs" in case_data:
                    paragraphs = [p for p in case_data["all_paragraphs"] if p.get("title") == title]

                if not paragraphs:
                    return None, []

                sorted_paras = sorted(paragraphs, key=extract_id_number)
                section_text = []
                for item in sorted_paras:
                    if isinstance(item, dict) and "text" in item:
                        cleaned_para = self.clean_text(item["text"])
                        if cleaned_para:
                            section_text.append(cleaned_para)
                
                merged_text = "\n\n".join(section_text) if section_text else None
                final_text = self.clean_text(merged_text) if merged_text else None
                return final_text, sorted_paras

            conclusion_text, conclusion_paras = extract_section("Conclusion")
            case_info["conclusion"] = conclusion_text
            case_info["conclusion_paragraphs"] = conclusion_paras

            reasoning_text, reasoning_paras = extract_section("Court's Reasoning")
            case_info["reasoning"] = reasoning_text
            case_info["reasoning_paragraphs"] = reasoning_paras

            return case_info

        except json.JSONDecodeError as e:
            error_msg = f"JSON decode error in {file_path}: {str(e)}"
            self.error_log.append(error_msg)
            raise
        except Exception as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            self.error_log.append(error_msg)
            raise

    def process_directory(self) -> None:
        """
        Process all JSON files in the input directory and extract conclusions.
        """
        print(f"\n📂 Scanning directory: {self.input_dir}")
        print("=" * 70)

        # Get all JSON files in the directory
        json_files = list(Path(self.input_dir).rglob("*.json"))

        if not json_files:
            print("⚠️  No JSON files found in the directory.")
            return

        print(f"📄 Found {len(json_files)} JSON files\n")

        for idx, file_path in enumerate(json_files, 1):
            try:
                print(
                    f"[{idx}/{len(json_files)}] Processing: {file_path.name}...",
                    end=" ",
                )

                conclusion_data = self.extract_conclusion_from_file(str(file_path))
                self.conclusions_data.append(conclusion_data)
                self.processed_files += 1

                has_conclusion = "✓" if conclusion_data.get("conclusion") else "⚠️"
                has_reasoning = "✓" if conclusion_data.get("reasoning") else "⚠️"
                print(f"Conclusion: {has_conclusion} | Reasoning: {has_reasoning}")

            except Exception as e:
                self.failed_files += 1
                print(f"✗ FAILED")

        print("\n" + "=" * 70)
        print(f"✓ Processing Complete:")
        print(f"  • Successfully processed: {self.processed_files}")
        print(f"  • Failed: {self.failed_files}")
        print(
            f"  • Total conclusions extracted: {len([d for d in self.conclusions_data if d.get('conclusion')])}"
        )
        print(
            f"  • Total reasoning extracted: {len([d for d in self.conclusions_data if d.get('reasoning')])}"
        )

    def save_conclusions(self, output_filename: str = "conclusions_data.json") -> str:
        """
        Save extracted conclusions to a JSON file.

        Args:
            output_filename: Name of the output file

        Returns:
            Path to the saved file
        """
        output_path = os.path.join(self.output_dir, output_filename)

        # Prepare the final data structure
        output_data = {
            "metadata": {
                "extraction_date": datetime.now().isoformat(),
                "total_cases": len(self.conclusions_data),
                "cases_with_conclusions": len(
                    [d for d in self.conclusions_data if d.get("conclusion")]
                ),
                "cases_with_reasoning": len(
                    [d for d in self.conclusions_data if d.get("reasoning")]
                ),
                "source_directory": self.input_dir,
                "processing_stats": {
                    "successfully_processed": self.processed_files,
                    "failed": self.failed_files,
                },
            },
            "conclusions": self.conclusions_data,
            "errors": self.error_log if self.error_log else [],
        }

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

        # Save to JSON file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Conclusions saved to: {output_path}")
        print(f"   File size: {os.path.getsize(output_path) / 1024:.2f} KB")

        return output_path

    def save_summary_report(
        self, output_filename: str = "conclusions_summary.json"
    ) -> str:
        """
        Save a summary report of conclusions (without full text).

        Args:
            output_filename: Name of the summary file

        Returns:
            Path to the saved file
        """
        output_path = os.path.join(self.output_dir, output_filename)

        summary_data = {
            "metadata": {
                "extraction_date": datetime.now().isoformat(),
                "total_cases": len(self.conclusions_data),
                "cases_with_conclusions": len(
                    [d for d in self.conclusions_data if d.get("conclusion")]
                ),
                "cases_with_reasoning": len(
                    [d for d in self.conclusions_data if d.get("reasoning")]
                ),
            },
            "case_summaries": [
                {
                    "case_id": case.get("case_id"),
                    "case_title": case.get("case_title"),
                    "url": case.get("url"),
                    "court_name": case.get("court_name"),
                    "has_conclusion": bool(case.get("conclusion")),
                    "has_reasoning": bool(case.get("reasoning")),
                    "conclusion_length": (
                        len(case.get("conclusion", "")) if case.get("conclusion") else 0
                    ),
                    "reasoning_length": (
                        len(case.get("reasoning", "")) if case.get("reasoning") else 0
                    ),
                    "conclusion_preview": (
                        (case.get("conclusion", "")[:200] + "...")
                        if case.get("conclusion")
                        else None
                    ),
                    "reasoning_preview": (
                        (case.get("reasoning", "")[:200] + "...")
                        if case.get("reasoning")
                        else None
                    ),
                }
                for case in self.conclusions_data
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)

        print(f"📋 Summary report saved to: {output_path}")

        return output_path

    def generate_statistics(self) -> Dict[str, Any]:
        """
        Generate statistics about the extracted conclusions.

        Returns:
            Dictionary with statistics
        """
        conclusions_with_text = [
            d for d in self.conclusions_data if d.get("conclusion")
        ]
        reasoning_with_text = [
            d for d in self.conclusions_data if d.get("reasoning")
        ]

        stats = {
            "total_cases": len(self.conclusions_data),
            "cases_with_conclusions": len(conclusions_with_text),
            "cases_without_conclusions": len(self.conclusions_data)
            - len(conclusions_with_text),
            "cases_with_reasoning": len(reasoning_with_text),
            "cases_without_reasoning": len(self.conclusions_data)
            - len(reasoning_with_text),
            "avg_conclusion_length": sum(
                len(d.get("conclusion", "")) for d in conclusions_with_text
            )
            / max(len(conclusions_with_text), 1),
            "max_conclusion_length": max(
                (len(d.get("conclusion", "")) for d in conclusions_with_text), default=0
            ),
            "min_conclusion_length": min(
                (
                    len(d.get("conclusion", ""))
                    for d in conclusions_with_text
                    if d.get("conclusion")
                ),
                default=0,
            ),
            "avg_reasoning_length": sum(
                len(d.get("reasoning", "")) for d in reasoning_with_text
            )
            / max(len(reasoning_with_text), 1),
            "max_reasoning_length": max(
                (len(d.get("reasoning", "")) for d in reasoning_with_text), default=0
            ),
            "min_reasoning_length": min(
                (
                    len(d.get("reasoning", ""))
                    for d in reasoning_with_text
                    if d.get("reasoning")
                ),
                default=0,
            ),
        }

        return stats

    def print_statistics(self) -> None:
        """Print statistics about extracted conclusions."""
        stats = self.generate_statistics()

        print("\n" + "=" * 70)
        print("📊 EXTRACTION STATISTICS")
        print("=" * 70)
        print(f"Total cases processed: {stats['total_cases']}")
        print(f"Cases with conclusions: {stats['cases_with_conclusions']}")
        print(f"Cases without conclusions: {stats['cases_without_conclusions']}")
        print(f"Cases with reasoning: {stats['cases_with_reasoning']}")
        print(f"Cases without reasoning: {stats['cases_without_reasoning']}")
        
        print(f"\nConclusion Length Statistics:")
        print(f"  • Average length: {stats['avg_conclusion_length']:.0f} characters")
        print(f"  • Maximum length: {stats['max_conclusion_length']} characters")
        print(f"  • Minimum length: {stats['min_conclusion_length']} characters")
        
        print(f"\nReasoning Length Statistics:")
        print(f"  • Average length: {stats['avg_reasoning_length']:.0f} characters")
        print(f"  • Maximum length: {stats['max_reasoning_length']} characters")
        print(f"  • Minimum length: {stats['min_reasoning_length']} characters")
        print("=" * 70 + "\n")


def main():
    """Main execution function."""

    # Configuration
    INPUT_DIRECTORY = "data/"  # Directory containing case JSON files
    OUTPUT_DIRECTORY = "data"  # Directory to save conclusions

    # Create extractor instance
    extractor = ConclusionExtractor(
        input_dir=INPUT_DIRECTORY, output_dir=OUTPUT_DIRECTORY
    )

    # Process all files
    extractor.process_directory()

    # Print statistics
    extractor.print_statistics()

    # Save conclusions
    extractor.save_conclusions("conclusions_data.json")

    # Save summary report
    extractor.save_summary_report("conclusions_summary.json")

    print("\n✅ Extraction completed successfully!")


if __name__ == "__main__":
    main()
