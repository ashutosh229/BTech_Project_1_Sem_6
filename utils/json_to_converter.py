import json
import csv
from pathlib import Path
from utils.config_loader import load_config

config = load_config()
REPO_ROOT = Path(config["REPO_ROOT"])


def json_folder_to_csv(input_dir: Path, output_csv: Path):
    rows = []
    all_fields = set()

    for json_file in input_dir.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Track source file
        data["_filename"] = json_file.name

        rows.append(data)
        all_fields.update(data.keys())

    if not rows:
        print(f"⚠️ No JSON files found in {input_dir}")
        return

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=sorted(all_fields))
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Converted {len(rows)} files → {output_csv}")


# Paths
bns_folder = REPO_ROOT / "data/bns_sections"
ips_folder = REPO_ROOT / "data/ipc_sections"

bns_csv = REPO_ROOT / "data/bns_sections.csv"
ips_csv = REPO_ROOT / "data/ipc_sections.csv"

# Run conversions
json_folder_to_csv(bns_folder, bns_csv)
json_folder_to_csv(ips_folder, ips_csv)
