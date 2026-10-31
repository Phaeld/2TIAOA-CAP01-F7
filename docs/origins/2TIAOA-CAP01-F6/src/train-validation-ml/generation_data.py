"""
Project: Multi-Agent Cardiac Risk Prediction System
AUTOR: Raphael da Silva RM561452
"""

from pathlib import Path

import numpy as np
import pandas as pd

np.random.seed(42)
N_SAMPLES = 5000

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = BASE_DIR / "data" / "synthetic_data.csv"


def generate_synthetic_data():

    df = pd.DataFrame({
        "middle_ages": np.random.normal(55, 12, N_SAMPLES).clip(18, 90),
        "system_load": np.random.uniform(30, 100, N_SAMPLES),
        "waiting_time": np.random.normal(45, 20, N_SAMPLES).clip(5, 180),
        "average_hr": np.random.normal(85, 15, N_SAMPLES).clip(50, 150),
        "average_spo2": np.random.normal(95, 3, N_SAMPLES).clip(70, 100),
        "systolic_bp": np.random.normal(125, 20, N_SAMPLES).clip(80, 200),
        "temperature": np.random.normal(24, 5, N_SAMPLES).clip(10, 40),
        "event_density": np.random.poisson(3, N_SAMPLES),
        "events_24h": np.random.poisson(2, N_SAMPLES),
        "resource_availability": np.random.uniform(20, 100, N_SAMPLES)
    })

    # Calculate the risk score
    risk_score = (
        (df["system_load"] > 80).astype(int)
        + (df["waiting_time"] > 60).astype(int)
        + (df["average_spo2"] < 92).astype(int)
        + (df["average_hr"] > 110).astype(int)
        + (df["events_24h"] > 4).astype(int)
        + (df["resource_availability"] < 40).astype(int)
    )

    # Define the binary target variable
    df["risk_peak"] = (risk_score >= 2).astype(int)

    return df


def main():

    df = generate_synthetic_data()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print("\nSYNTHETIC DATA GENERATED SUCCESSFULLY")
    print(f"Total records: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    print(f"File saved: {OUTPUT_PATH}")

    print("\nFirst five records:")
    print(df.head())


if __name__ == "__main__":
    main()
