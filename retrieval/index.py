import json
import logging
import os
from pathlib import Path

import faiss
import numpy as np
import torch
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
INDEX_DIR = os.path.join(DATA_DIR, "index")
INDEX_FILE = os.path.join(INDEX_DIR, "legal_fact_index.faiss")
ID_MAP_FILE = os.path.join(PROCESSED_DIR, "case_indices.json")
MODEL_NAME = "law-ai/InLegalBERT"

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def extract_facts(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return ""

    elements = data.get("elements_by_title", {})
    sections = [
        "Fact",
        "Issues",
        "Petitioner's Arguments",
        "Respondent's Arguments",
        "Analysis of the law",
        "Court's Reasoning",
        "Analysis",
    ]

    chunks = []
    for section in sections:
        if section in elements:
            text = " ".join(item.get("text", "") for item in elements[section]).strip()
            if text:
                chunks.append(text[:1500])

    return " ".join(chunks)[:2500].lower()


def _mean_pool(last_hidden_state, attention_mask):
    mask = attention_mask.unsqueeze(-1)
    masked = last_hidden_state * mask
    return masked.sum(dim=1) / mask.sum(dim=1).clamp(min=1)


def encode_texts(texts, batch_size=16):
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, local_files_only=True)
    model = AutoModel.from_pretrained(MODEL_NAME, local_files_only=True)
    model.eval()

    all_embeddings = []
    for start in tqdm(range(0, len(texts), batch_size), desc="Encoding"):
        batch = texts[start : start + batch_size]
        with torch.no_grad():
            inputs = tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            )
            outputs = model(**inputs)
            pooled = _mean_pool(outputs.last_hidden_state, inputs["attention_mask"])
            all_embeddings.append(pooled.cpu().numpy())
    return np.vstack(all_embeddings).astype("float32")


def build_index():
    json_files = sorted(Path(DATA_DIR).rglob("*.json"))
    case_ids = []
    texts = []

    logging.info("Extracting retrieval text from %d judgments...", len(json_files))
    for path in tqdm(json_files, desc="Collecting corpus"):
        text = extract_facts(path)
        if text:
            case_ids.append(path.stem)
            texts.append(text)

    if not texts:
        logging.error("No usable retrieval text found.")
        return

    logging.info("Encoding %d case narratives with %s...", len(texts), MODEL_NAME)
    embeddings = encode_texts(texts)

    os.makedirs(INDEX_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, INDEX_FILE)

    with open(ID_MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(case_ids, f, indent=2)

    logging.info("Saved FAISS index with %d cases.", len(case_ids))
    logging.info("Index: %s", INDEX_FILE)
    logging.info("ID Map: %s", ID_MAP_FILE)


if __name__ == "__main__":
    build_index()
