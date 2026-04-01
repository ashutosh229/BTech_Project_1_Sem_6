# 📂 Legal Intelligence: Module Index

### 1. `con/` (Case Object Notation)
- `schema.py`: Standardized **Legal JSON contract.**
- `builder.py`: Maps raw text to CON objects.
- `feature_builder.py`: Constructs the **Phi-Vector ($\Phi$)** for ML models.

### 2. `retrieval/` (RAG Intelligence)
- `search.py`: **InLegalBERT** + **FAISS** retrieval branch.
- Finding "Successful Siblings" and precedents.

### 3. `models/` (Reasoning Branches)
- `contradiction/`: **NLI-Style** symbolic contradiction detection.
- `missing_evidence/`: **Gap Analysis** against KG-defined patterns.
- `judgment/`: **XGBoost Inference Engine** and Training scripts.

### 4. `pipelines/` (Data Ingestion)
- `pipeline1_old_cases/`: Scraping, parsing, and cleaning of India Kanoon JSONs.
- `evidence_extractor.py`: Multi-cluster evidence identification via **K-Means / NLP**.

### 5. `data/` (Storage)
- `con/`: Saved standardized case objects.
- `dataset/`: Training matrices (`X, y`).
- `processed/`: Serialized models and metadata.
- `results/`: Completed intelligence reports.

### 6. `outputs/` (Presentation)
- `plots/`: Automatically generated research-grade visualizations.
- Dashboard PNGs for bias and trends.
