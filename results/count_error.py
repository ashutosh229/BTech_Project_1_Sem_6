#!/usr/bin/env python3
"""Scan workspace JSON files for a specific error and save a summary JSON.

Usage:
  python3 docs/count_error.py --dir /path/to/search --out /path/to/output.json

Defaults search one level above this script (repository root) and writes
error_summary.json there.
"""
import os
import json
import argparse

TARGET_ERROR = "Judgments div not found (unexpected layout)"

def scan_jsons(search_dir):
    total = 0
    matched = []
    for root, _dirs, files in os.walk(search_dir):
        for fname in files:
            if fname.lower().endswith('.json'):
                total += 1
                path = os.path.join(root, fname)
                try:
                    with open(path, 'r', encoding='utf-8') as fh:
                        data = json.load(fh)
                except Exception:
                    # skip files that are not valid JSON or unreadable
                    continue
                if isinstance(data, dict) and data.get('error') == TARGET_ERROR:
                    matched.append(os.path.relpath(path, search_dir))
    return total, matched

def main():
    default_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    default_out = os.path.join(default_dir, 'error_summary.json')

    p = argparse.ArgumentParser(description='Count JSON files with a specific error message')
    p.add_argument('--dir', default=default_dir, help='Directory to search (defaults to workspace root)')
    p.add_argument('--out', default=default_out, help='Output JSON file path')
    args = p.parse_args()

    search_dir = os.path.abspath(args.dir)
    total, matched = scan_jsons(search_dir)

    summary = {
        'total_json_files': total,
        'error_count': len(matched),
        'error_files': matched,
        'error_message': TARGET_ERROR
    }

    with open(args.out, 'w', encoding='utf-8') as outfh:
        json.dump(summary, outfh, indent=2, ensure_ascii=False)

    print(f"Wrote summary to {args.out}: {summary['error_count']} of {summary['total_json_files']}")

if __name__ == '__main__':
    main()
