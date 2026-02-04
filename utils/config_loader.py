import json
from pathlib import Path


def load_config():
    repo_root = Path(__file__).parent.parent
    config_file_path = f"{repo_root}/config.json"
    with open(config_file_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    config["REPO_ROOT"] = f"{repo_root}"
    return config
