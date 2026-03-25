# Project Execution Plan: Causal Evidence Intelligence System

## 🎯 Objective
To build a knowledge-guided system that identifies "Missing Evidence" by comparing weak cases (dismissed due to lack of evidence) with similar strong cases (successful due to present evidence), and then ranks the importance of that evidence.

---

## 📅 Technical Roadmap

### **Step 1: Induction Phase (Evidence Mining & Normalization)**
- [x] **Task 1.1: Evidence Miner (Regex)**  
    - Create a regex scanner for reliable markers (scientific, procedural, witness, deeds).  
    - Refined to reduce false positives (word boundaries, tense check).
- [x] **Task 1.2: Semantic Embedding (InLegalBERT)**  
    - Map extracted strings into high-dimensional legal semantic space.
- [x] **Task 1.3: Evidence Clustering (HDBSCAN)**  
    - Automagically group strings like "Post-mortem" and "PM Report" into canonical ID clusters.
- [/] **Task 1.4: Multi-Hot Vectorization**  
    - Convert every case into a binary vector based on cluster presence. (RUNNING)
- **Artifact:** `results/evidence_normalization_map.json`, `results/case_evidence_matrix.csv`

### **Step 2: Identifying the Weak Links**
- [x] **Task 2.1: Weak Case Filter**  
    - Isolate cases that "failed" due to lack of evidence (benefit of doubt, failed to prove).
    - Found 497 cases out of 9,703 scanned.
- **Artifact:** `results/failed_cases_index.json`
*   **Keywords:** *'lack of evidence', 'insufficient evidence', 'benefit of doubt', 'not proved', 'prosecution failed to corroborate'*.
*   **Verification:** Cross-check that these cases have a "Dismissed/Acquitted" outcome.

### **Step 3: Causal Comparison (The "Reasoning" Phase)**
**Goal:** Identify which evidence was the "Differentiator" between a win and a loss.
*   **Fact Indexing:** Load the `primary_facts` embeddings into a **FAISS** vector database.
*   **Retrieval:** For a "Weak Case" $W$, find the top 5 most similar "Strong Cases" $S$ (Successful).
*   **Differential Calculation:** Compute the set difference: `MissingEvidence = Clusters(S) - Clusters(W)`.
*   **Output:** A list of "Candidate Missing Evidence" for every failed case.

### **Step 4: Importance Ranking Model (The "Learning" Phase)**
**Goal:** A predictive model that ranks evidence impact globally and locally.
*   **Global Training:** Train an **XGBoost or Random Forest** classifier where:
    *   $X$: Evidence Binary Vectors
    *   $y$: Case Outcome (0 or 1)
*   **Feature Importance:** Use **SHAP (Shapley Values)** to calculate exactly how much "lift" each evidence cluster (e.g., *Forensic Report*) adds to the probability of winning.
*   **Recommendation Engine:** For a new case $C$, predict the outcome and output: *"You have a 40% win probability. Adding a 'Corroborating Witness' cluster will increase it to 85%."*

---

## 🏗 Repository & Task Organization

| Module | Team / Lead | Files |
| :--- | :--- | :--- |
| **Data Foundry** | Team A | `evidence_extractor.py`, `cluster_evidence.py` |
| **Similarity Engine** | Team B | `faiss_index.py`, `retrieve_similar.py` |
| **Reasoning Layer** | Team B | `weak_case_filter.py`, `missing_evidence.py` |
| **Causal Ranker** | Shared | `importance_model.py`, `shap_explainer.py` |

---

## 📈 Current Project State (Knowledge of `data/` dir)
1.  **Dataset Ready:** ~12k JSON files with Rhetorical Roles are currently unignored in `.gitignore`.
2.  **Structure Validated:** JSON schema contains `elements_by_title` (Analysis, Reasoning, Conclusion).
3.  **Next Immediate Step:** Run a master script to extract raw evidence lists from all 12k files and prepare them for the **Step 1 Clustering**.

---

### 📝 Step 1: Deep Dive - Evidence Representation Pipeline

#### **Task 1.1: The "Evidence Miner" (`extract_all_evidence.py`)**
*   **Action:** Run a massive regex-based scan over all 12,000 `.json` files in the `data/` directory.
*   **Optimization:** Targeted extraction from `Reasoning` and `Analysis` sections ONLY. 
*   **Regex Inventory:** Keywords include `(report|memo|certificate|statement|document|memo|FIR|sheet|declaration|receipt|notice|panchnama|exhibit)`.
*   **Output:** `unique_evidence_pool.csv` mapping `case_id` to `raw_evidence_string`.

#### **Task 1.2: Legal Embedding & Contextual Normalization**
*   **Model:** Use `law-ai/InLegalBERT` via `sentence-transformers`. 
*   **Semantic Check:** Ensure "PW-1 deposition" and "Statement of Witness 1" are mapped to the same vector space. 

#### **Task 1.3: Discovery of $N$ Categories (HDBSCAN Clustering)**
*   **Action:** Unsupervised clustering of the ~1M raw strings extracted. 
*   **Auto-Clustering:** Use **HDBSCAN** to automatically determine the number of distinct evidence types (~100 clusters). 
*   **Mapping:** Create `normalization_map.json` mapping `raw_string` $\to$ `cluster_id`.

#### **Task 1.4: Multi-Hot Case Vectorization**
*   **Process:** For each Case ID, convert its list of evidence strings into a single binary vector. 
*   **Vector Shape:** `[1, 0, 1, ..., 0]` of length $N$ (where $N = $ number of clusters).
*   **Final Repository Structure:** Store the resulting vectors as a Parquet file for high-speed model training.

---
**Status:** 🏗 Plan Documented. 🚀 Ready for Implementation.
