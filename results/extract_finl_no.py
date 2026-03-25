#!/usr/bin/env python3
"""Extract trailing numeric ID from filenames listed in error_summary.json
and save results to error_ids.json.
"""
import os
import json
import re

HERE = os.path.abspath(os.path.dirname(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
SUMMARY = os.path.join(ROOT, 'error_summary.json')
OUT = os.path.join(ROOT, 'error_ids.json')

def extract_trailing_number(basename):
    m = re.search(r"(\d+)$", basename)
    return m.group(1) if m else None

def main():
    if not os.path.exists(SUMMARY):
        print(f"Summary not found: {SUMMARY}")
        return
    with open(SUMMARY, 'r', encoding='utf-8') as fh:
        data = json.load(fh)

    files = data.get('error_files', [])
    ids = []
    mapping = {}
    for p in files:
        base = os.path.splitext(os.path.basename(p))[0]
        num = extract_trailing_number(base)
        ids.append(num)
        mapping[p] = num

    out = {
        'total_error_files': len(files),
        'extracted_ids': ids,
        'file_to_id': mapping
    }

    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)

    print(f"Wrote {OUT} with {len(ids)} entries")

if __name__ == '__main__':
    main()
