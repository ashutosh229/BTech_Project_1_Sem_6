import json
import re
from pathlib import Path

def extract_num_from_id(item):
    m = re.search(r'\d+', item.get("id", ""))
    return int(m.group()) if m else float("inf")

def clean_text(text):
    if not isinstance(text, str):
        return text
    # collapse whitespace: spaces, tabs, newlines
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


for path in Path('.').glob('*.json'):
    print(f'Parsing {path.name}')

    with path.open(encoding='utf-8') as f:
        data = json.load(f)

    # ---- elements_by_title ----
    for section, items in data.get("elements_by_title", {}).items():
        if isinstance(items, list):
            items.sort(key=extract_num_from_id)
            for item in items:
                if "text" in item:
                    item["text"] = clean_text(item["text"])

    # ---- all_blockquotes ----
    if isinstance(data.get("all_blockquotes"), list):
        data["all_blockquotes"].sort(key=extract_num_from_id)
        for bq in data["all_blockquotes"]:
            if "text" in bq:
                bq["text"] = clean_text(bq["text"])

    # ---- save back ----
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

print("Sorted and whitespace-cleaned all JSON files")
