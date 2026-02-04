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
