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
                "This notebook visualizes the experiments and results from the **Induction** and **Targeting** phases of the Legal Evidence Pipeline. Key goals:\n",
                "1. Understand the distribution of 'Weak Cases' in the 10,000 judgment corpus.\n",
                "2. Analyze evidence density across different legal categories.\n",
                "3. Identify the 'Causal Gap' between successful and failed cases."
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
                "We scanned **9,703 judgments** to identify cases that were dismissed due to evidentiary weaknesses (e.g., 'benefit of doubt')."
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
                "sizes = [success_count, weak_count]\n",
                "colors = ['#4CAF50', '#F44336']\n",
                "\n",
                "plt.figure(figsize=(8, 8))\n",
                "plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors, explode=(0, 0.1))\n",
                "plt.title('Indian Legal Corpus Breakdown (9,703 Cases)', fontsize=15)\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 🔬 Section 2: Evidence Mining Density\n",
                "Results from the **Evidence Miner (Task 1.1)** showing the count of markers found per category in the 500-case pilot."
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
                "cat_counts.columns = ['Category', 'Mentions']\n",
                "\n",
                "sns.barplot(data=cat_counts, x='Mentions', y='Category', hue='Category', palette='viridis', legend=False)\n",
                "plt.title('Evidence Marker Yield by Category (Pilot Set)', fontsize=15)\n",
                "plt.xlabel('Total Mentions Found')\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 🧠 Section 3: The Causal Gap Analysis\n",
                "We compare the probability of findind an evidence marker in a **Success Case** vs a **Weak Case**."
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
                "    'cluster_0': 'Medical/FSL',\n",
                "    'cluster_1': 'PW Testimony',\n",
                "    'cluster_2': 'Contracts',\n",
                "    'cluster_3': 'Memos',\n",
                "    'cluster_4': 'FIR/PM Reports',\n",
                "    'cluster_5': 'Land Deeds'\n",
                "}\n",
                "\n",
                "stats = matrix_df.groupby('Case Status')[cluster_cols].mean().reset_index()\n",
                "stats_melted = stats.melt(id_vars='Case Status', var_name='Cluster', value_name='Probability')\n",
                "stats_melted['Cluster Name'] = stats_melted['Cluster'].map(cluster_names)\n",
                "\n",
                "plt.figure(figsize=(14, 7))\n",
                "sns.barplot(data=stats_melted, x='Cluster Name', y='Probability', hue='Case Status')\n",
                "plt.title('The Contention Signal: Probability of Evidence Being Discussed', fontsize=15)\n",
                "plt.ylabel('Likelihood of Mention in Judgment')\n",
                "plt.xticks(rotation=45)\n",
                "plt.show()"
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
