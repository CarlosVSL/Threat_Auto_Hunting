#!/usr/bin/env python3
"""
model_utils.py: Utility functions for model evaluation and reporting.
"""
import json
from sklearn.metrics import classification_report


def evaluate_model(y_true, y_pred):
    """
    Compute classification metrics and return a dict with precision, recall, f1-score, support for each class.
    """
    report = classification_report(y_true, y_pred, output_dict=True)
    return report


def save_classification_report(report: dict, path: str):
    """
    Save classification report dict to a JSON file at the specified path.
    """
    with open(path, 'w') as f:
        json.dump(report, f, indent=2)
# Utility functions
