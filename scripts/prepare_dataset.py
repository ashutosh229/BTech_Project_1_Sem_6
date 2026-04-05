import os

import pandas as pd

from con.feature_builder import LegalFeatureBuilder, outcome_to_binary


SUMMARY_PATH = "data/processed/corpus_intelligence_summary.csv"
OUTPUT_DIR = "data/dataset"


def _output_paths(summary_path):
    summary_name = os.path.splitext(os.path.basename(summary_path))[0]
    if summary_name == "corpus_intelligence_summary":
        return (
            os.path.join(OUTPUT_DIR, "final_phi_features.csv"),
            os.path.join(OUTPUT_DIR, "X_features.csv"),
            os.path.join(OUTPUT_DIR, "y_labels.csv"),
        )
    suffix = summary_name.replace("corpus_intelligence_summary", "").strip(".-_")
    suffix = suffix or summary_name
    return (
        os.path.join(OUTPUT_DIR, f"final_phi_features.{suffix}.csv"),
        os.path.join(OUTPUT_DIR, f"X_features.{suffix}.csv"),
        os.path.join(OUTPUT_DIR, f"y_labels.{suffix}.csv"),
    )


def build_phi_matrix(summary_path=SUMMARY_PATH):
    if not os.path.exists(summary_path):
        print(f"⚠️ Summary dataset not found at {summary_path}. Run batch_process.py first.")
        return None

    df = pd.read_csv(summary_path)
    builder = LegalFeatureBuilder()
    feature_names = builder.feature_names

    missing = [col for col in feature_names if col not in df.columns]
    if missing:
        print("⚠️ Summary file is missing canonical Phi columns.")
        print("Missing:", ", ".join(missing[:15]), "..." if len(missing) > 15 else "")
        print("Run batch_process.py again to regenerate the summary with canonical features.")
        return None

    if "true_outcome" not in df.columns:
        print("⚠️ Summary file is missing true_outcome. Run batch_process.py again.")
        return None

    final_dataset_path, x_path, y_path = _output_paths(summary_path)
    dataset = df[["case_id", "true_outcome"] + feature_names].copy()
    dataset["label"] = dataset["true_outcome"].apply(outcome_to_binary)
    dataset = dataset[dataset["label"].notna()].copy()
    dataset["label"] = dataset["label"].astype(int)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    dataset.to_csv(final_dataset_path, index=False)
    dataset[feature_names].to_csv(x_path, index=False)
    dataset[["label"]].to_csv(y_path, index=False)

    print(f"✅ Final Phi dataset ready: {len(dataset)} samples.")
    print(f"💾 Saved: {final_dataset_path}")
    return dataset


if __name__ == "__main__":
    build_phi_matrix()
