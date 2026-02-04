from utils.config_loader import load_config
import os

config = load_config()

REPO_ROOT = config["REPO_ROOT"]
BASE_URL = config["BASE_URL"]
INDEX_URL = config["INDEX_URL"]
HEADERS = config["HEADERS"]

OUTPUT_DIR = os.path.join(REPO_ROOT, config["OUTPUT_DIR"])

print(f"Output directory is set to: {OUTPUT_DIR}")
print(f"Repo root is: {REPO_ROOT}")
print("DIR EXISTS:", os.path.exists(OUTPUT_DIR))
