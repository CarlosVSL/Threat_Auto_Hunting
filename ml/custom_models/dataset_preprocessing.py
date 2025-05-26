#!/usr/bin/env python3
"""
dataset_preprocessing.py: Load and preprocess datasets for ML models.
"""
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


def load_dataset(path: str) -> pd.DataFrame:
    """
    Load dataset from CSV file and return a pandas DataFrame.
    """
    df = pd.read_csv(path)
    return df


def preprocess_features(df: pd.DataFrame) -> np.ndarray:
    """
    Preprocess features:
      - Impute missing numeric values with median.
      - Scale numeric features to zero mean and unit variance.
      - One-hot encode categorical features.
    Returns a numpy array of processed features.
    """
    # Separate numeric and categorical columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

    # Impute numeric features
    num_imputer = SimpleImputer(strategy='median')
    X_num = num_imputer.fit_transform(df[numeric_cols])

    # Scale numeric features
    scaler = StandardScaler()
    X_num_scaled = scaler.fit_transform(X_num)

    # Encode categorical features
    if categorical_cols:
        df_cat = df[categorical_cols].fillna('missing')
        X_cat = pd.get_dummies(df_cat, drop_first=True).values
        # Concatenate numeric and categorical arrays
        X_preprocessed = np.hstack([X_num_scaled, X_cat])
    else:
        X_preprocessed = X_num_scaled

    return X_preprocessed

