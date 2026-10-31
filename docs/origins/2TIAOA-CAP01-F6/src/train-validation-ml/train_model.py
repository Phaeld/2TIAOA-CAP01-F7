"""
Project: Multi-Agent Cardiac Risk Prediction System
AUTOR: Raphael da Silva RM561452
"""

from pathlib import Path

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = BASE_DIR / "data" / "synthetic_data.csv"
MODEL_PATH = BASE_DIR / "models" / "risk_model.joblib"
TEST_DATA_PATH = BASE_DIR / "data" / "test_data.csv"

TARGET_COLUMN = "risk_peak"


def train_model():

    # Load the synthetic dataset
    df = pd.read_csv(DATA_PATH)

    # Separate input features and target variable
    X = df.drop(columns=[TARGET_COLUMN])
    y = df[TARGET_COLUMN]

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    # Initialize the Random Forest classifier
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )

    # Train the classification model
    model.fit(X_train, y_train)

    # Create output directories
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    TEST_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Save the trained model and feature names
    model_artifact = {
        "model": model,
        "features": X.columns.tolist(),
        "target": TARGET_COLUMN
    }

    joblib.dump(model_artifact, MODEL_PATH)

    # Save the untouched test dataset
    test_df = X_test.copy()
    test_df[TARGET_COLUMN] = y_test

    test_df.to_csv(
        TEST_DATA_PATH,
        index=False,
        encoding="utf-8"
    )

    print("\nMODEL TRAINING COMPLETED")
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")
    print(f"Input features: {X.shape[1]}")
    print(f"Model saved: {MODEL_PATH}")
    print(f"Test data saved: {TEST_DATA_PATH}")


if __name__ == "__main__":
    train_model()
