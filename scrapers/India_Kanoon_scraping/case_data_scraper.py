#!/usr/bin/env python3
"""
Indian Kanoon Scraper (JS-safe)
Uses Playwright to correctly retrieve dynamically injected title attributes
"""

import os
from playwright.sync_api import sync_playwright,TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
import json
from typing import Dict
import time
import random
from urllib.parse import urlparse

def normalize_doc_url(href: str) -> str | None:
    path = urlparse(href).path
    parts = path.strip("/").split("/")

    if len(parts) >= 2 and parts[0] in ("doc", "docfragment"):
        doc_id = parts[1]
        return f"https://indiankanoon.org/doc/{doc_id}/"

    return None
class IndianKanoonScraper:
    def __init__(self, page):
        self.page = page
    

    def fetch_page(self, url: str, retries=2) -> str | None:
     for attempt in range(retries + 1):


        try:
            self.page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )
            self.page.wait_for_timeout(1500)
            return self.page.content()

        except PlaywrightTimeout:
            print(f"⚠️ Timeout ({attempt+1}/{retries+1}) → {url}")
            if attempt == retries:
                return None
            self.page.wait_for_timeout(3000)

        

    def scrape_document(self, url: str) -> Dict:
        html = self.fetch_page(url)
        if not html:
         return None
        soup = BeautifulSoup(html, "html.parser")

        result = {
            "url": url,
            "page_title": "",
            "court_name": "",
            "case_title": "",
            "elements_by_title": {},
            "all_paragraphs": [],
            "all_blockquotes": [],
        }

        # <title> tag (now reliably populated)
        title_tag = soup.find("title")
        if title_tag:
            result["page_title"] = title_tag.get_text(strip=True)

        judgments_div = soup.find("div", class_="judgments")
        if not judgments_div:
            return {"error": "Judgments div not found (unexpected layout)"}

        # Court name
        court = judgments_div.find("h3", class_="docsource")
        if court:
            result["court_name"] = court.get_text(strip=True)

        # Case title
        case = judgments_div.find("h2", class_="doc_title")
        if case:
            result["case_title"] = case.get_text(strip=True)

        # Helper
        def get_title(tag):
            return tag.get("title").strip() if tag.get("title") else "Uncategorized"

        # ---- PARAGRAPHS ----
        for p in judgments_div.find_all("p"):
            data = {
                "tag": "p",
                "id": p.get("id", ""),
                "class": " ".join(p.get("class", [])),
                "title": get_title(p),
                "text": p.get_text(strip=True),
            }
            result["all_paragraphs"].append(data)
            result["elements_by_title"].setdefault(data["title"], []).append(data)

        # ---- BLOCKQUOTES ----
        for bq in judgments_div.find_all("blockquote"):
            data = {
                "tag": "blockquote",
                "id": bq.get("id", ""),
                "class": " ".join(bq.get("class", [])),
                "title": get_title(bq),
                "style": bq.get("style", ""),
                "text": bq.get_text(strip=True),
            }
            result["all_blockquotes"].append(data)
            result["elements_by_title"].setdefault(data["title"], []).append(data)

        return result

    def save_json(self, data: Dict, filename: str):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_text(self, data: Dict, filename: str):
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"URL: {data['url']}\n")
            f.write(f"Page Title: {data['page_title']}\n")
            f.write(f"Court: {data['court_name']}\n")
            f.write(f"Case: {data['case_title']}\n")
            f.write("=" * 80 + "\n\n")

            for title, elems in data["elements_by_title"].items():
                f.write(f"\n=== {title} ({len(elems)}) ===\n\n")
                for e in elems:
                    f.write(f"[{e['tag']}] {e['text']}\n\n")


def main():
    with open("browse.json", "r", encoding="utf-8") as f:
        courts = json.load(f)

    years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        scraper = IndianKanoonScraper(page)

        for item in courts:
            court = item["slug"]

            for year in years:
                print(f"Visiting {court} - {year}...")
                

                
                if court == "supremecourt" and year == 2015:
                     continue

                with open(f"{court}_{year}.json", "r", encoding="utf-8") as g:
                    data = json.load(g)
                for entry in data:
                    url = entry["url"]
                    doc_url = normalize_doc_url(url)
                    doc_id = doc_url.rstrip("/").split("/")[-1]
                    
                    outfile = f"docs/{court}_{year}_{doc_id}.json"
                    if os.path.exists(outfile):
                     continue

                    doc_data = scraper.scrape_document(f"{doc_url}")
                    scraper.save_json(doc_data, f"docs/{court}_{year}_{doc_id}.json")    

                    
                time.sleep(random.uniform(1.5, 3.0))

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
