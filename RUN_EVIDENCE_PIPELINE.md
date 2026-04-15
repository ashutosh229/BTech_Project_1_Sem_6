# ⚖️ Running the Evidence Pipeline End-to-End

This document outlines the step-by-step instructions to run the **Evidence Pipeline** (Induction Phase) sequentially from scratch, as well as how to use the pipeline components within the unified inference system.

The Evidence Pipeline relies on multiple scripts located within the `models/missing_evidence/` directory.

---

## Phase 1: Pre-computation and Modeling (Training/Setup)

Before running the dashboard or individual predictions, the core indices and models for weak case detection and evidence priority need to be built. Make sure your Python virtual environment is activated and requirements are installed.

*Note: These scripts expect your raw json case files to be in `data/` and will output artifacts to `data/processed/` or `results/`.*

### Step 1: Weak Case Detection
Finds and scores weak/failed cases using semantic and text pattern extraction, outputting probabilistic scores for every case.

```bash
python models/missing_evidence/weak_case_detection.py
```
**Artifacts Generated:**
- `data/processed/failed_cases_index.json`
- `data/processed/weak_case_scores.json`
- `data/processed/weak_case_scores.csv`
- `data/processed/weak_case_model.joblib`

### Step 2: Causal Importance Ranking
Uses Random Forest and Gradient Boosting to measure the statistical importance of different evidence clusters (e.g., Medical Reports, Witness Testimony) regarding successful vs. weak outcomes.

```bash
python models/missing_evidence/importance.py
```
**Artifacts Generated:**
- `data/processed/outcome_predictor.joblib`
- `outputs/causal_ranking.json`

### Step 3: Evidentiary Gap Analysis
Aggregates frequencies to print out the differential probability gap (Success vs. Weak) for each canonical evidence cluster based on the weak-case scores calculated in Step 1.

```bash
python models/missing_evidence/gap_analysis.py
```
*(Prints a human-readable table of Causal Importance and Differential Gaps directly to the terminal).*

### Step 4: Failure Mode Diagnostics
Analyzes the weak cases for textual failure modes (e.g., Delay, Contradiction, Non-Production of evidence) and produces statistical summaries.

```bash
python models/missing_evidence/diagnostics.py
```
**Artifacts Generated:**
- `results/failure_diagnostics.csv`

---

## Phase 2: Live Inference (Using the Pipeline)

Once the models and indices are generated from Phase 1, you can run the evidence pipeline on single cases or batches. The missing evidence recommendations are seamlessly integrated into the unified architecture.

### Option A: Single Case Inference
You can observe the outcome of missing evidence detection inside the unified pipeline for a specific case. This calls `models/missing_evidence/recommendation.py` under the hood.

```bash
python main_pipeline.py
```
*Output will print the "Missing Evidence", "Current Evidence", and "Similar Cases" to the console as part of the JSON output.*

### Option B: Batch Corpus Processing
To run the evidence analysis and evidence recommendations against the entire historical corpus (9,000+ cases):

```bash
python batch_process.py
```
Wait for the terminal progress bar to complete. 
**Artifacts Generated:**
- `data/processed/corpus_intelligence_summary.csv` (contains missing evidence counts and metrics per case).
