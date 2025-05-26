#!/usr/bin/env python3
"""
train_classifier.py: Train a RandomForest classifier to detect lateral movement based on endpoint and network log features.
"""
import os
import argparse
import joblib

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Custom preprocessing and utils
from dataset_preprocessing import load_dataset, preprocess_features
from model_utils import evaluate_model, save_classification_report


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train a classifier for lateral movement detection"
    )
    parser.add_argument(
        "--data-path", required=True,
        help="Path to CSV file containing features and label."
    )
    parser.add_argument(
        "--output-dir", default=".",
        help="Directory to save the trained model and report"
    )
    parser.add_argument(
        "--model-name", default="lateral_movement_model.pkl",
        help="Filename for the saved model"
    )
    parser.add_argument(
        "--test-size", type=float, default=0.2,
        help="Proportion of data to use for testing"
    )
    parser.add_argument(
        "--n-estimators", type=int, default=100,
        help="Number of trees in the RandomForest"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Load raw dataset
    df = load_dataset(args.data_path)

    # Separate features and label
    X_raw = df.drop(columns=["label"])
    y = df["label"]

    # Preprocess features (scaling, encoding, feature engineering)
    X = preprocess_features(X_raw)

    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=42, stratify=y
    )

    # Initialize and train classifier
    clf = RandomForestClassifier(
        n_estimators=args.n_estimators,
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)

    # Predict and evaluate
    y_pred = clf.predict(X_test)
    report = evaluate_model(y_test, y_pred)

    # Save classification report as JSON
    os.makedirs(args.output_dir, exist_ok=True)
    report_path = os.path.join(args.output_dir, "classification_report.json")
    save_classification_report(report, report_path)

    # Save trained model
    model_path = os.path.join(args.output_dir, args.model_name)
    joblib.dump(clf, model_path)
    print(f"Trained model saved to {model_path}")
    print(f"Classification report saved to {report_path}")


if __name__ == "__main__":
    main()
