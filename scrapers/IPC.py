import os
import json
import re
from matplotlib import table
from matplotlib import table
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from utils.config_loader import load_config

config = load_config()

REPO_ROOT = config["REPO_ROOT"]
BASE_URL = config["BASE_URL"]
INDEX_URL = config["INDEX_URL"]
HEADERS = config["HEADERS"]

OUTPUT_DIR = f"{REPO_ROOT}/{config['OUTPUT_DIR']}"


def clean(text):
    return " ".join(text.strip().split()) if text else ""


def get_section_links():
    res = requests.get(INDEX_URL, headers=HEADERS)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "lxml")
    links = []

    for a in soup.select("span.sectionlink"):
        parent = a.find_parent("a")
        if parent and parent.get("href"):
            full_url = urljoin(BASE_URL, parent["href"])
            links.append(full_url)

    return links


def scrape_section(url):
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "lxml")

    data = {
        "type": "IPC",
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

    table = soup.find("table", class_="search")
    if not table:
        return data

    # ---- Chapter ----
    chapter_th = table.find("th", class_="title")
    if chapter_th:
        match = re.search(r"Chapter\s+([IVXLCDM]+)", chapter_th.get_text())
        if match:
            data["chapter"] = match.group(1)

    # ---- Section number + Title ----
    head_row = table.find("tr", class_="mys-head")
    if head_row:
        h2s = head_row.find_all("h2")
        if len(h2s) >= 2:
            data["section"] = clean(h2s[0].get_text().replace("S.", ""))
            data["title"] = clean(h2s[1].get_text())

    # ---- Description ----
    desc_row = table.find("tr", class_="mys-desc")
    if desc_row:
        data["description"] = clean(desc_row.get_text())

    # ---- Classification tables (Offence, Punishment, Cognizance etc.) ----
    for sch in table.find_all("table", class_="sch"):
        headers = [clean(th.get_text()).lower() for th in sch.find_all("th")]
        values = [clean(td.get_text()) for td in sch.find_all("td")]

        if "offence" in headers and "punishment" in headers:
            if len(values) >= 2:
                data["offense"] = values[0]
                data["punishment"] = values[1]

        if "cognizance" in headers and "bail" in headers and "triable by" in headers:
            if len(values) >= 3:
                data["cognizance"] = values[0]
                data["bail"] = values[1]
                data["triable_by"] = values[2]

    # ---- Compoundable ----
    comp_table = table.find("table", summary=re.compile("Compoundable", re.I))
    if comp_table:
        h2 = comp_table.find("h2")
        if h2:
            data["compoundable"] = clean(h2.get_text())

    return data


def save_json(data):
    if not data["section"]:
        return

    filename = f"{data['section']}_IPC.json"
    path = os.path.join(OUTPUT_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    links = get_section_links()
    print(f"Found {len(links)} sections")

    for i, link in enumerate(links, 1):
        try:
            print(f"[{i}] {link}")
            data = scrape_section(link)
            save_json(data)
        except Exception as e:
            print(f"❌ Failed: {link} | {e}")


if __name__ == "__main__":
    main()
