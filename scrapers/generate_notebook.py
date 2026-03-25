import json
import os

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# ⚖️ Legal Intelligence System: Analysis & Insights\n",
                "Developed by Antigravity AI Assistant\n",
                "\n",
                "## 🎯 Objective\n",
                "This notebook visualizes the experiments and results from the **Induction** and **Targeting** phases. Key goals:\n",
                "1. Understand the distribution of 'Weak Cases' in the 10,000 judgment corpus.\n",
                "2. Analyze evidence density across different legal categories.\n",
                "3. Identify the 'Causal Gap' between successful and failed cases.\n",
                "4. **Similarity Retrieval:** Use FAISS to find successful peers for a weak case."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import pandas as pd\n",
                "import json\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "import numpy as np\n",
                "import faiss\n",
                "\n",
                "# Set Styling\n",
                "sns.set_theme(style='whitegrid', palette='muted')\n",
                "plt.rcParams['figure.figsize'] = (12, 6)\n",
                "\n",
                "RESULTS_DIR = '/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/results'"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 📊 Section 1: Corpus Composition\n",
                "Scanning **9,703 judgments** to identify the 5.1% 'Weak Case' subset."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "with open(f'{RESULTS_DIR}/failed_cases_index.json', 'r') as f:\n",
                "    weak_cases = json.load(f)\n",
                "\n",
                "total_cases = 9703\n",
                "weak_count = len(weak_cases)\n",
                "success_count = total_cases - weak_count\n",
                "\n",
                "labels = ['Success', 'Weak Cases']\n",
                "plt.pie([success_count, weak_count], labels=labels, autopct='%1.1f%%', startangle=140, colors=['#4CAF50', '#F44336'])\n",
                "plt.title('Indian Legal Corpus Breakdown')\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 🔬 Section 2: Evidence Mining Density\n",
                "Results from the **Evidence Miner (Task 1.1)**."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "df_pilot = pd.read_csv(f'{RESULTS_DIR}/pilot_evidence_results.csv')\n",
                "cat_counts = df_pilot['category'].value_counts().reset_index()\n",
                "sns.barplot(data=cat_counts, x='count', y='category', hue='category', palette='viridis', legend=False)\n",
                "plt.title('Marker Yield by Category')\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 🧠 Section 3: The Causal Gap Analysis\n",
                "Comparing evidence frequency in **Success** vs **Weak** cases."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "matrix_df = pd.read_csv(f'{RESULTS_DIR}/case_evidence_matrix.csv')\n",
                "failed_ids = [c['case_id'] for c in weak_cases]\n",
                "matrix_df['Case Status'] = matrix_df['case_id'].isin(failed_ids).map({True: 'Weak', False: 'Success'})\n",
                "\n",
                "cluster_cols = [c for c in matrix_df.columns if c.startswith('cluster_')]\n",
                "cluster_names = {\n",
                "    'cluster_0': 'Medical/FSL', 'cluster_1': 'PW Testimony', 'cluster_2': 'Contracts', \n",
                "    'cluster_3': 'Memos', 'cluster_4': 'FIR/PM Reports', 'cluster_5': 'Land Deeds'\n",
                "}\n",
                "\n",
                "stats = matrix_df.groupby('Case Status')[cluster_cols].mean().reset_index().melt(id_vars='Case Status')\n",
                "stats['Cluster Name'] = stats['variable'].map(cluster_names)\n",
                "sns.barplot(data=stats, x='Cluster Name', y='value', hue='Case Status')\n",
                "plt.xticks(rotation=45)\n",
                "plt.title('Evidence Probability Comparison')\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 🚀 Section 4: The Recommendation Probe (Similarity Match)\n",
                "Matching a weak case with 5 successful peers."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "index = faiss.read_index(f'{RESULTS_DIR}/legal_fact_index.faiss')\n",
                "with open(f'{RESULTS_DIR}/case_indices.json', 'r') as f:\n",
                "    case_ids = json.load(f)\n",
                "\n",
                "test_id = weak_cases[0]['case_id']\n",
                "q_idx = case_ids.index(test_id)\n",
                "q_vec = index.reconstruct(q_idx).reshape(1, -1)\n",
                "D, I = index.search(q_vec, 15)\n",
                "\n",
                "success_peers = [case_ids[idx] for idx in I[0] if case_ids[idx] not in failed_ids][:5]\n",
                "q_row = matrix_df[matrix_df['case_id'] == test_id].iloc[0]\n",
                "p_rows = matrix_df[matrix_df['case_id'].isin(success_peers)]\n",
                "\n",
                "print(f\"📌 Weak Case: {test_id} vs {len(success_peers)} Peers\")\n",
                "comparison = []\n",
                "for c in cluster_cols:\n",
                "    comparison.append({ 'Evidence Type': cluster_names.get(c, c), 'Query Presence': '✅' if q_row[c]==1 else '❌', 'Peer Usage (%)': f'{p_rows[c].mean()*100:.1f}%' })\n",
                "pd.DataFrame(comparison)"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.10.12"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open('/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/results/Legal_Intelligence_Analysis.ipynb', 'w') as f:
    json.dump(notebook, f, indent=2)
