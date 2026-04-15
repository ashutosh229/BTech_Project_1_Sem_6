# ⚖️ Running the Full Pipeline End-to-End

This document outlines the **complete execution sequence** from raw case ingestion to trained ML model with research-grade evaluation metrics.

---

## Prerequisites

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Phase 1: Evidence Index Construction

### Step 1: Weak Case Detection
Builds a probabilistic weak-case index using TF-IDF + Logistic Regression ensemble.

```bash
python models/missing_evidence/weak_case_detection.py
```
**Outputs:** `data/processed/failed_cases_index.json`, `weak_case_scores.json`, `weak_case_model.joblib`

### Step 2: Causal Importance Ranking
Trains ensemble models (GradientBoosting + RandomForest + LogReg) to rank evidence clusters.

```bash
python models/missing_evidence/importance.py
```
**Outputs:** `data/processed/outcome_predictor.joblib`, `outputs/causal_ranking.json`

### Step 3: Evidentiary Gap Analysis
Prints the differential gap (Success vs. Weak) per evidence cluster.

```bash
python models/missing_evidence/gap_analysis.py
```

### Step 4: Failure Mode Diagnostics
Classifies weak cases by failure mode (Delay, Contradiction, Non-Production).

```bash
python models/missing_evidence/diagnostics.py
```
**Outputs:** `results/failure_diagnostics.csv`

---

## Phase 2: Batch Corpus Processing (Φ-Vector Generation)

Runs the full unified pipeline on all 9,700+ cases to produce the corpus summary CSV with Φ-features.

```bash
python batch_process.py
```
**Outputs:** `data/processed/corpus_intelligence_summary.csv`

---

## Phase 3: Dataset Extraction

Extracts the clean ML dataset from the corpus summary. Filters to binary labels (Allowed/Dismissed), drops ambiguous cases.

```bash
python scripts/prepare_dataset.py
```
**Outputs:**
- `data/dataset/final_phi_features.csv` (full dataset with labels)
- `data/dataset/X_features.csv` (features only)
- `data/dataset/y_labels.csv` (labels only)

---

## Phase 4: Model Training & Evaluation

Trains XGBoost with 5-fold stratified cross-validation, produces confusion matrix, feature importance plot, and a JSON metrics report.

```bash
python models/judgment/train.py
```
**Outputs:**
- `data/processed/judgment_model.joblib`
- `outputs/plots/confusion_matrix.png`
- `outputs/plots/feature_importance.png`
- `outputs/training_metrics.json`

---

## Phase 5: Ablation Study (Research Validation)

Tests the incremental lift of each Φ-vector block:
- **A:** Context only → **B:** + Evidence → **C:** + Gap → **D:** + Conflict → **E:** Full Pipeline

```bash
python models/judgment/train_ablation.py
```
**Outputs:**
- `outputs/ablation_results.json`
- `outputs/plots/ablation_study.png`

---

## Phase 6: Single Case Inference

Run the full trained pipeline on a single case:

```bash
python main_pipeline.py
```

---

## Quick Reference: Execution Order

```
1. weak_case_detection.py     → Build weak-case index
2. importance.py              → Rank evidence importance
3. batch_process.py           → Generate corpus Φ-vectors
4. scripts/prepare_dataset.py → Extract clean ML dataset
5. models/judgment/train.py   → Train + Evaluate model
6. train_ablation.py          → Run ablation study
7. main_pipeline.py           → Live inference
```
