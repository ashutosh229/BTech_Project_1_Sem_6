#!/usr/bin/env python3
"""
Indian Kanoon Browse Scraper (JS-safe)
Extracts all browse links and their slugs
"""

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from typing import List, Dict
from urllib.parse import urlparse
import time
class IndianKanoonScraper:
    def __init__(self, page):
        self.page = page
    

    def fetch_page(self, url: str) -> str:
        self.page.goto(url, wait_until="networkidle", timeout=60000)
        self.page.wait_for_timeout(1500)
        return self.page.content()
        
    def scrape_search(self, url: str) -> List[Dict]:
        html = self.fetch_page(url)
        soup = BeautifulSoup(html, "html.parser")

        results = []
        seen = set()

        for h4 in soup.find_all("h4", class_="result_title"):
            a = h4.find("a", href=True)
            if not a:
                continue

            href = a["href"]

            # Normalize path
            

            
            results.append({
                        "url": href
                    })

        return results


    def save_json(self, data, filename: str):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)



    


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
                print(f"Scraping {court} {year}")

                url0 = (
                    f"https://indiankanoon.org/search/"
                    f"?formInput=doctypes%3A%20{court}%20year%3A%20{year}&pagenum=0"
                )
                url1 = (
                    f"https://indiankanoon.org/search/"
                    f"?formInput=doctypes%3A%20{court}%20year%3A%20{year}&pagenum=1"
                )

                data = scraper.scrape_search(url0) + scraper.scrape_search(url1)

                with open(f"{court}_{year}.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)

                time.sleep(2)  # IMPORTANT: avoid bans

        context.close()
        browser.close()
if __name__ == "__main__":
    main()            


   
    


    
