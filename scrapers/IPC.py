import os
import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

with open("config.json", "r") as f:
    config = json.load(f)

BASE_URL = config["BASE_URL"]
INDEX_URL = config["INDEX_URL"]
OUTPUT_DIR = config["OUTPUT_DIR"]
HEADERS = config["HEADERS"]
