#!/usr/bin/env python3
"""
Indian Kanoon Browse Scraper (JS-safe)
Extracts all browse links and their slugs
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from typing import List, Dict


class IndianKanoonScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless

    def fetch_page(self, url: str) -> str:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(1500)
            html = page.content()
            browser.close()
            return html

    def scrape_browse(self, url: str) -> List[Dict]:
        html = self.fetch_page(url)
        soup = BeautifulSoup(html, "html.parser")

        results = []

        for a in soup.find_all("a", href=True):
            href = a["href"]

            # Only keep browse links
            if not href.startswith("/browse/"):
                continue

            parts = href.strip("/").split("/")
            slug = parts[-1] if len(parts) > 1 else ""

            if slug:
                results.append({
                                         "slug": slug,
                    
                })

        return results

    def save_json(self, data, filename: str):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    url = "https://indiankanoon.org/browse/"
    scraper = IndianKanoonScraper(headless=True)

    print("Scraping browse page...")
    data = scraper.scrape_browse(url)

    scraper.save_json(data, "browse.json")

    print(f"✓ Done — {len(data)} entries saved")


if __name__ == "__main__":
    main()
