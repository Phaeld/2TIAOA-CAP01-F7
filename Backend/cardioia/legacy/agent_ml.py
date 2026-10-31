
"""
Project: Multi-Agent Cardiac Risk Prediction System
Module: Machine Learning Prediction Agent
Description: Loads the trained model and predicts synthetic risk peaks.
"""

from pathlib import Path

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "models" / "risk_model.joblib"


class MLPredictionAgent:

    def __init__(self, model_path=MODEL_PATH):

        # Load the trained model artifact
        artifact = joblib.load(model_path)

        self.model = artifact["model"]
        self.features = artifact["features"]
        self.target = artifact["target"]

    def validate_input(self, case_data):

        # Validate the input data structure
        if not isinstance(case_data, dict):
            raise TypeError("Input data must be a dictionary.")

        # Check for missing or unexpected features
        missing_features = [
            feature for feature in self.features
            if feature not in case_data
        ]

        unexpected_features = [
            feature for feature in case_data
            if feature not in self.features
        ]

        if missing_features:
            raise ValueError(
                f"Missing features: {missing_features}"
            )

        if unexpected_features:
            raise ValueError(
                f"Unexpected features: {unexpected_features}"
            )

        # Convert input values to a DataFrame
        input_df = pd.DataFrame([case_data])
        input_df = input_df[self.features]

        # Validate numeric and finite values
        for feature in self.features:

            input_df[feature] = pd.to_numeric(
                input_df[feature],
                errors="raise"
            )

        if input_df.isna().any().any():
            raise ValueError("Input contains missing values.")

        import numpy as np

        if not np.isfinite(input_df.to_numpy()).all():
            raise ValueError("Input contains non-finite values.")

        return input_df

    def predict(self, case_data):

        # Validate and prepare input features
        input_df = self.validate_input(case_data)

        # Predict the binary target class
        predicted_class = int(
            self.model.predict(input_df)[0]
        )

        # Get the positive-class probability
        class_index = list(self.model.classes_).index(1)

        risk_probability = float(
            self.model.predict_proba(input_df)[0][class_index]
        )

        # Assign a descriptive risk level
        risk_level = "HIGH" if predicted_class == 1 else "LOW"

        # Return a structured prediction result
        result = {
            "agent": "MLPredictionAgent",
            "predicted_class": predicted_class,
            "risk_probability": round(risk_probability, 4),
            "risk_percentage": round(risk_probability * 100, 2),
            "risk_level": risk_level,
            "input_data": input_df.iloc[0].to_dict()
        }

        return result
