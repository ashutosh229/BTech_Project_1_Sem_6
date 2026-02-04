import os
import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from utils.config_loader import load_config

config = load_config()

BASE_URL = config["BASE_URL"]
INDEX_URL = config["INDEX_URL"]
OUTPUT_DIR = config["OUTPUT_DIR"]
HEADERS = config["HEADERS"]
REPO_ROOT = config["REPO_ROOT"]


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
