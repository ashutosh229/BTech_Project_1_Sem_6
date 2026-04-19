import os
import json
import re
import numpy as np
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModel
import sys

# Add project root to path for imports
sys.path.append(os.getcwd())

from pipelines.pipeline1_old_cases.parse_case_json import parse_real_case_json

# --- Configuration ---
DATA_DIR = "data"
OUTPUT_FILE = "outputs/shareable_legal_vectors.json"
MODEL_NAME = "law-ai/InLegalBERT"
BATCH_SIZE = 8
MAX_DOCS = None # Limit for demonstration/initial run, set to None for all

def normalize_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

def generate_embeddings(texts, tokenizer, model):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    all_embeddings = []
    
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i + BATCH_SIZE]
        encoded_input = tokenizer(batch_texts, padding=True, truncation=True, max_length=512, return_tensors='pt').to(device)
        
        with torch.no_grad():
            model_output = model(**encoded_input)
            
        embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
        all_embeddings.append(embeddings.cpu().numpy())
        
    return np.vstack(all_embeddings)

def main():
    print(f"🚀 Starting data transformation and embedding process...")
    
    # 1. Collect and Structure Data
    json_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    json_files.sort()
    
    if MAX_DOCS:
        json_files = json_files[:MAX_DOCS]
        
    structured_data = []
    texts_to_embed = []
    
    print(f"📦 Processing {len(json_files)} cases...")
    for filename in tqdm(json_files, desc="Parsing Cases"):
        file_path = os.path.join(DATA_DIR, filename)
        try:
            # Parse raw JSON into standard format
            case_data = parse_real_case_json(file_path)
            
            # Extract metadata and core content
            case_id = case_data.get("case_id")
            title = case_data.get("case_title")
            outcome = case_data.get("outcome")
            facts = normalize_text(case_data.get("primary_facts", ""))
            
            if not facts:
                continue
                
            entry = {
                "metadata": {
                    "case_id": case_id,
                    "title": title,
                    "outcome": outcome,
                    "source_file": filename
                },
                "content": facts,
                "embedding": None # Will fill later
            }
            
            structured_data.append(entry)
            texts_to_embed.append(facts)
            
        except Exception as e:
            print(f"⚠️ Error parsing {filename}: {e}")
            continue
            
    if not structured_data:
        print("❌ No valid data found to process.")
        return
        
    # 2. Load Model and Generate Embeddings
    print(f"🧠 Loading {MODEL_NAME} and generating embeddings...")
    try:
        # Try local first, then download if allowed
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModel.from_pretrained(MODEL_NAME)
        model.eval()
    except Exception as e:
        print(f"⚠️ Could not load model: {e}")
        return
        
    embeddings = generate_embeddings(texts_to_embed, tokenizer, model)
    
    # 3. Map Embeddings back to Data
    for i, entry in enumerate(structured_data):
        # Convert numpy array to list for JSON serialization
        entry["embedding"] = embeddings[i].tolist()
        
    # 4. Save to JSON
    print(f"💾 Saving structured vector data to {OUTPUT_FILE}...")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, indent=2)
        
    print(f"✅ Successfully processed {len(structured_data)} cases.")
    print(f"📍 Output file: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
