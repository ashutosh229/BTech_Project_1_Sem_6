# ⚖️ Legal Intelligence System: Evidence Pipeline

## 🎯 Project Objective
This project implements the **Induction Phase** of a legal intelligence system. It uses NLP and Semantic Clustering (InLegalBERT + HDBSCAN) to identify evidence patterns in 10,000 judgments, isolate "Weak Cases" dismissed due to evidentiary failures, and suggest missing evidence through similarity retrieval.

## 📅 Roadmap Execution: Completed

### **Step 1: Evidence Representation (Induction)**
- [x] **Task 1.1: Evidence Miner (Regex)**  
    - Scanned 10,000 cases for scientific, procedural, and legal markers.
- [x] **Task 1.2: Semantic Embedding (InLegalBERT)**  
    - Vectorized ~19,000 raw evidence strings into high-dimensional space.
- [x] **Task 1.3: Evidence Clustering (HDBSCAN)**  
    - Grouped strings into 6 canonical clusters (Medical, Testimony, Contracts, etc.).
- [x] **Task 1.4: Multi-Hot Vectorization**  
    - Converted every case into a binary bit-vector for computational analysis.
- **Artifacts:** `results/evidence_normalization_map.json`, `results/case_evidence_matrix.csv`

### **Step 2: Identifying the Weak Links (Targeting)**
- [x] **Task 2.1: Weak Case Filter**  
    - Isolated 497 cases (5.1%) dismissed due to 'insufficient evidence' or 'benefit of doubt'.
- **Artifact:** `results/failed_cases_index.json`

### **Step 3: Finding Similar Cases (Semantic Retrieval)**
- [x] **Task 3.1: Fact Summarizer & Extractor**  
    - Extracted core factual narratives from the corpus.
- [x] **Task 3.2: FAISS Semantic Indexing**  
    - Built a vector index of 8,700+ useable factual summaries.
- [x] **Task 3.3: Peer Evidence Recommendation**  
    - **Logic:** Find successful siblings for a weak case and identify its missing evidence.
- **Artifact:** `results/legal_fact_index.faiss`, `results/case_indices.json`, `scrapers/recommend_evidence.py`

### **Step 4: Causal Priority & Analysis Dashboard**
- [x] **Task 4.1: Statistical Ranking (Random Forest)**  
    - Ranked 'Witness Testimony' as the #1 factor (35% importance) in case dismissal.
- [x] **Task 4.2: Visual Intelligence Dashboard (Jupyter)**  
    - Full visualization of "The Contention Signal" and the "Richness Gap".
- **Artifact:** `results/causal_ranking.json`, `results/Legal_Intelligence_Analysis.ipynb`

---

**🎉 PROJECT STATUS: 100% FINALIZED**
- **Repository:** All scripts and results pushed to GitHub.
- **Deployment Ready:** The system is prepared to ingest new judgments and provide "Missing Evidence" recommendations out-of-the-box.
