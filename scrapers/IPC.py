import os
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from utils.config_loader import load_config


# -------------------- CONFIG --------------------

config = load_config()

REPO_ROOT = config["REPO_ROOT"]
BASE_URL = config["BASE_URL"]
INDEX_URL = config["INDEX_URL"]
HEADERS = config["HEADERS"]

OUTPUT_DIR = os.path.join(REPO_ROOT, config["OUTPUT_DIR"])
print("DIR EXISTS:", os.path.exists(OUTPUT_DIR))


# -------------------- SESSION (FAST + SAFE) --------------------

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

retry = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
)
SESSION.mount("https://", HTTPAdapter(max_retries=retry))


# -------------------- HELPERS --------------------


def clean(text: str) -> str:
    return " ".join(text.strip().split()) if text else ""


# -------------------- SCRAPING --------------------


def get_section_links():
    res = SESSION.get(INDEX_URL)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "lxml")
    links = []

    for span in soup.select("span.sectionlink"):
        parent = span.find_parent("a")
        if parent and parent.get("href"):
            links.append(urljoin(BASE_URL, parent["href"]))

    # deduplicate while preserving order
    return list(dict.fromkeys(links))


def scrape_section(url: str) -> dict:
    res = SESSION.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "lxml")

    data = {
        "type": "",
        "section": "",
        "chapter": "",
        "title": "",
        "description": "",
        "offense": "",
        "punishment": "",
        "cognizance": "",
        "bail": "",
        "triable_by": "",
        "compoundable": "",
    }

    search_div = soup.find("div", class_="search")
    if not search_div:
        return data

    main_table = search_div.find("table")
    if not main_table:
        return data

    section_th = main_table.select_one("th.sec")
    if section_th:
        data["type"] = section_th.get_text()

    # ---- Chapter ----
    chapter_th = main_table.select_one("th.title.fill")
    if chapter_th:
        match = re.search(r"Chapter\s+([IVXLCDM]+)", chapter_th.get_text())
        if match:
            data["chapter"] = match.group(1)

    # ---- Section number + Title ----
    head_row = main_table.find("tr", class_="mys-head")
    if head_row:
        h2s = head_row.find_all("h2")
        if len(h2s) >= 2:
            data["section"] = clean(h2s[0].get_text().replace("S.", ""))
            data["title"] = clean(h2s[1].get_text())

    # ---- Description ----
    desc_row = main_table.find("tr", class_="mys-desc")
    if desc_row:
        data["description"] = clean(desc_row.get_text())

    # ---- Classification tables ----
    for sch in main_table.find_all("table", class_="sch"):
        headers = [clean(th.get_text()).lower() for th in sch.find_all("th")]
        values = [clean(td.get_text()) for td in sch.find_all("td")]

        if "offence" in headers and "punishment" in headers and len(values) >= 2:
            data["offense"] = values[0]
            data["punishment"] = values[1]

        if (
            "cognizance" in headers
            and "bail" in headers
            and "triable by" in headers
            and len(values) >= 3
        ):
            data["cognizance"] = values[0]
            data["bail"] = values[1]
            data["triable_by"] = values[2]

    # ---- Compoundable / Non-Compoundable ----
    comp_table = main_table.find("table", summary=re.compile("Compoundable", re.I))

    if comp_table:
        sch = comp_table.find("table", class_="sch")
        if sch:
            td = sch.find("td")
            if td:
                # Compoundable case
                data["compoundable"] = clean(td.get_text())
            else:
                # Not compoundable case
                h2 = sch.find("h2")
                if h2:
                    data["compoundable"] = clean(h2.get_text())

    return data


# -------------------- STORAGE --------------------


def save_json(data: dict):
    if not data["section"]:
        return

    filename = f"{data['section']}_IPC.json"
    path = os.path.join(OUTPUT_DIR, filename)

    # skip if already scraped
    if os.path.exists(path):
        return

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# -------------------- WORKER --------------------


def process_section(link: str, index: int):
    data = scrape_section(link)
    save_json(data)
    return f"[{index}] ✔ Section {data['section']}"


# -------------------- MAIN --------------------


def main():
    links = get_section_links()
    print(f"Found {len(links)} IPC sections")

    MAX_WORKERS = 10  # safe + fast

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(process_section, link, i) for i, link in enumerate(links, 1)
        ]

        for future in as_completed(futures):
            try:
                print(future.result())
            except Exception as e:
                print(f"❌ Error: {e}")

print("Scraping completed!")
if __name__ == "__main__":
    main()
