import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import hdbscan
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def perform_clustering(input_csv, output_map_json, model_name='law-ai/InLegalBERT'):
    """
    Groups extracted evidence strings into semantic clusters using LegalBERT + HDBSCAN.
    """
    try:
        # 1. Load the pilot extraction results
        df = pd.read_csv(input_csv)
        if 'matched_text' not in df.columns:
            logging.error(f"Matched text column not found in {input_csv}")
            return

        unique_texts = df['matched_text'].unique().tolist()
        logging.info(f"🧬 Found {len(unique_texts)} unique evidence strings. Embedding using {model_name}...")

        # 2. Generate Semantic Embeddings
        # Note: This may take a few minutes depending on CPU/GPU
        model = SentenceTransformer(model_name)
        embeddings = model.encode(unique_texts, show_progress_bar=True)

        # 3. Perform HDBSCAN Clustering
        # min_cluster_size=2: We want to catch even small clusters of specific evidence
        logging.info("🛰️ Running HDBSCAN to discover evidence categories...")
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=2, 
            metric='euclidean', 
            prediction_data=True,
            cluster_selection_method='eom'
        )
        cluster_labels = clusterer.fit_predict(embeddings)

        # 4. Create Normalization Map (String -> Cluster ID)
        normalization_map = {}
        cluster_previews = {} # For logging analysis

        for text, label in zip(unique_texts, cluster_labels):
            label_id = int(label)
            normalization_map[text] = label_id
            
            if label_id != -1: # Ignore noise/outliers for preview
                if label_id not in cluster_previews:
                    cluster_previews[label_id] = []
                if len(cluster_previews[label_id]) < 5:
                    cluster_previews[label_id].append(text)

        # 5. Save the Map
        with open(output_map_json, 'w', encoding='utf-8') as f:
            json.dump(normalization_map, f, indent=2, ensure_ascii=False)

        logging.info(f"✅ Clustering Complete.")
        num_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        logging.info(f"📊 Identified {num_clusters} semantic clusters.")
        logging.info(f"🗺️ Normalization map saved to: {output_map_json}")

        # Final Summary for Inference
        logging.info("--- Sample Clusters Identified ---")
        for cid, samples in list(cluster_previews.items())[:5]:
            logging.info(f"Cluster {cid}: {samples}")

    except Exception as e:
        logging.error(f"❌ Error during clustering: {e}")

if __name__ == "__main__":
    INPUT_FILE = "/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/results/pilot_evidence_results.csv"
    OUTPUT_FILE = "/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/results/evidence_normalization_map.json"
    
    perform_clustering(INPUT_FILE, OUTPUT_FILE)
