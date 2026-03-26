import json
import os

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# ⚖️ Legal Intelligence: The Ultimate Causal Dashboard\n",
                "Created by Antigravity AI Assistant\n",
                "\n",
                "## 🧬 Objective\n",
                "This dashboard is a comprehensive visual autopsy of 10,000 legal judgments. It uses **InLegalBERT** to map rhetorical evidence and **Random Forest Machine Learning** to quantify the causal forces of failure."
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
                "sns.set_theme(style='whitegrid', context='talk')\n",
                "plt.rcParams['figure.figsize'] = (14, 8)\n",
                "RESULTS_DIR = '/home/amaydixit11/Desktop/dev/Legal-Intelligence-System/results'\n",
                "\n",
                "cluster_names = {\n",
                "    'cluster_0': 'Medical/FSL', 'cluster_1': 'Witness Testimony', 'cluster_2': 'Agreements', \n",
                "    'cluster_3': 'Memos', 'cluster_4': 'FIR/PM Reports', 'cluster_5': 'Property Deeds'\n",
                "}"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 📊 Section 1: The Corpus Evidence Fingerprint\n",
                "We compare the 'Richness' of evidence in **Success** vs **Weak** cases. \n",
                "\n",
                "**The Contra-Signal Discovery:** Weak cases actually mention evidence *more* often because they are points of intense debate or failure."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "matrix_df = pd.read_csv(f'{RESULTS_DIR}/case_evidence_matrix.csv')\n",
                "with open(f'{RESULTS_DIR}/failed_cases_index.json', 'r') as f:\n",
                "    weak_cases = json.load(f)\n",
                "failed_ids = [c['case_id'] for c in weak_cases]\n",
                "matrix_df['Status'] = matrix_df['case_id'].isin(failed_ids).map({True: 'Weak/Failed', False: 'Success/Strong'})\n",
                "\n",
                "cols = [c for c in matrix_df.columns if c.startswith('cluster_')]\n",
                "stats = matrix_df.groupby('Status')[cols].mean().reset_index().melt(id_vars='Status')\n",
                "stats['Cluster Name'] = stats['variable'].map(cluster_names)\n",
                "\n",
                "sns.barplot(data=stats, x='Cluster Name', y='value', hue='Status', palette=['#5D9C59', '#DF2E38'])\n",
                "plt.title('Evidence Probability: Success vs failure', fontsize=18)\n",
                "plt.ylabel('Probability of Mention (%)')\n",
                "plt.xticks(rotation=45)\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 🏆 Section 2: Causal Importance (Predictive Weight)\n",
                "Which evidence cluster is the #1 predictor of a legal outcome?"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "with open(f'{RESULTS_DIR}/causal_ranking.json', 'r') as f:\n",
                "    ranking = json.load(f)\n",
                "rank_df = pd.DataFrame(ranking)\n",
                "sns.barplot(data=rank_df, x='Importance Score (%)', y='Evidence Cluster', palette='viridis')\n",
                "plt.title('Statistical Ranking of Legal Importance', fontsize=18)\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 🕵️‍♂️ Section 3: Failure Mode Diagnostics\n",
                "Why did the 497 weak cases fail? Is it a factual problem or a procedural (police) error?"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "diag_df = pd.read_csv(f'{RESULTS_DIR}/failure_diagnostics.csv')\n",
                "# Handle stringified lists in CSV\n",
                "import ast\n",
                "diag_df['modes'] = diag_df['failure_modes'].apply(lambda x: ast.literal_eval(x) if pd.notnull(x) else [])\n",
                "modes_exploded = diag_df.explode('modes')\n",
                "mode_counts = modes_exploded['modes'].value_counts().reset_index()\n",
                "\n",
                "sns.barplot(data=mode_counts, x='count', y='modes', palette='flare')\n",
                "plt.title('Failure Mode Distribution: Why Cases Fall Apart', fontsize=18)\n",
                "plt.xlabel('Number of Weak Cases Affected')\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 📈 Section 4: Evidence Synergies (Correlations)\n",
                "Certain evidence clusters build on each other. High correlation indicates 'Corroboration Linkages'."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "corr = matrix_df[cols].corr()\n",
                "corr.columns = [cluster_names.get(c) for c in corr.columns]\n",
                "corr.index = [cluster_names.get(c) for c in corr.index]\n",
                "sns.heatmap(corr, annot=True, cmap='coolwarm', center=0)\n",
                "plt.title('Evidence Corroboration Synergy (Correlations)', fontsize=18)\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## ⚖️ Section 5: Legal Area Heatmap (Criminal vs Civil)\n",
                "Does the 'Evidence Signature' change between property disputes and criminal trials?"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "with open(f'{RESULTS_DIR}/legal_area_comparison.json', 'r') as f:\n",
                "    area_comp = json.load(f)\n",
                "comp_list = []\n",
                "for area, data in area_comp.items():\n",
                "    for cluster, imp in data.items():\n",
                "        comp_list.append({'Legal Area': area.capitalize(), 'Evidence Type': cluster_names.get(cluster), 'Importance': imp*100})\n",
                "df_area = pd.DataFrame(comp_list)\n",
                "sns.move_legend(sns.barplot(data=df_area, x='Evidence Type', y='Importance', hue='Legal Area', palette=['#3A1078', '#3795BD']), \"upper right\")\n",
                "plt.title('Evidence Rulebook: Criminal vs Civil Comparison', fontsize=18)\n",
                "plt.xticks(rotation=45)\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 🛰️ Section 6: Live Recommendation Simulation\n",
                "Using the FAISS Vector Engine to find similar successful 'Winning Siblings'."
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
                "target_case = failed_ids[0]\n",
                "q_idx = case_ids.index(target_case)\n",
                "q_vec = index.reconstruct(q_idx).reshape(1,-1)\n",
                "D, I = index.search(q_vec, 15)\n",
                "\n",
                "peers = [case_ids[idx] for idx in I[0] if case_ids[idx] not in failed_ids][:5]\n",
                "peer_rows = matrix_df[matrix_df['case_id'].isin(peers)]\n",
                "q_row = matrix_df[matrix_df['case_id'] == target_case].iloc[0]\n",
                "\n",
                "print(f\"📌 Analysis for Case: {target_case}\")\n",
                "print(f\"✅ Similarity Check: Found {len(peers)} successful peers for diagnostic.\")\n",
                "recs = []\n",
                "for c in cols:\n",
                "    recs.append({'Evidence Type': cluster_names.get(c), 'Current Case': '✅' if q_row[c]==1 else '❌', 'Peer Importance (%)': f'{peer_rows[c].mean()*100:.1f}%'})\n",
                "pd.DataFrame(recs)"
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
