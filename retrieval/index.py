import os
import json
import logging
import torch
import numpy as np
import faiss
from pathlib import Path
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# --- Configuration ---
DATA_DIR = "/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/data"
RESULTS_DIR = "/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/results"
INDEX_FILE = f"{RESULTS_DIR}/legal_fact_index.faiss"
ID_MAP_FILE = f"{RESULTS_DIR}/case_indices.json"
MODEL_NAME = 'law-ai/InLegalBERT'

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def extract_facts(json_path):
    """
    Priority: 1. Fact 2. Analysis and Reasoning sections
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except: return ""
    
    elements = data.get("elements_by_title", {})
    # Priority sections for factual summaries
    sections = [
        "Fact", 
        "Analysis of the law", 
        "Court's Reasoning",
        "Analysis"
    ]
    
    fact_text = ""
    for s in sections:
        if s in elements:
            fact_text = " ".join([item.get("text", "") for item in elements[s]]).strip()
            if len(fact_text) > 200: 
                break # Found a substantial section
    
    # Return first 1000 chars to avoid memory explode
    return fact_text[:1000].lower()

def build_index():
    # 1. Load Legal BERT Model
    print(f"🛰️ Loading {MODEL_NAME} for factual embedding...")
    model = SentenceTransformer(MODEL_NAME)
    
    # 2. Collect Factual narratives
    json_files = list(Path(DATA_DIR).glob('*.json'))
    case_ids = []
    texts = []
    
    print(f"📄 Extracting facts from {len(json_files)} judgments...")
    for path in tqdm(json_files):
        text = extract_facts(path)
        if text:
            case_ids.append(path.stem)
            texts.append(text)
    
    if not texts:
        print("❌ No useable facts found in the corpus.")
        return

    # 3. Create Embeddings
    print(f"🧠 Encoding {len(texts)} case narratives into 768-dim space...")
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)
    embeddings = np.array(embeddings).astype('float32')

    # 4. Build FAISS Index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # 5. Save Artifacts
    faiss.write_index(index, INDEX_FILE)
    with open(ID_MAP_FILE, 'w') as f:
        json.dump(case_ids, f)
        
    print(f"✅ FAISS Semantic Index created with {len(case_ids)} nodes.")
    print(f"💾 Index: {INDEX_FILE}")
    print(f"💾 ID Map: {ID_MAP_FILE}")

if __name__ == "__main__":
    build_index()
