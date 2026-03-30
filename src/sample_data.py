from __future__ import annotations

from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError


RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
CUSTOMERS_PATH = RAW_DIR / "credit_profiles.csv"

CUSTOMERS = [
    {
        "customer_id": "CRED-1001",
        "name": "Ana Souza",
        "score": 742,
        "score_band": "good",
        "on_time_payment_ratio": 0.97,
        "credit_utilization_pct": 28,
        "recent_late_payments": 0,
        "active_accounts": 6,
        "hard_inquiries_6m": 1,
        "negative_records": 0,
        "main_drivers": "Strong payment consistency and low recent delinquency.",
    },
    {
        "customer_id": "CRED-1002",
        "name": "Bruno Lima",
        "score": 618,
        "score_band": "fair",
        "on_time_payment_ratio": 0.83,
        "credit_utilization_pct": 71,
        "recent_late_payments": 2,
        "active_accounts": 4,
        "hard_inquiries_6m": 4,
        "negative_records": 1,
        "main_drivers": "High utilization and late payments are pulling the score down.",
    },
    {
        "customer_id": "CRED-1003",
        "name": "Carla Mendes",
        "score": 556,
        "score_band": "poor",
        "on_time_payment_ratio": 0.71,
        "credit_utilization_pct": 88,
        "recent_late_payments": 4,
        "active_accounts": 3,
        "hard_inquiries_6m": 5,
        "negative_records": 2,
        "main_drivers": "Multiple recent delinquencies, very high utilization, and negative records.",
    },
]


def ensure_sample_data() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    should_rebuild = not CUSTOMERS_PATH.exists()

    if CUSTOMERS_PATH.exists() and CUSTOMERS_PATH.stat().st_size == 0:
        should_rebuild = True

    if CUSTOMERS_PATH.exists() and not should_rebuild:
        try:
            preview = pd.read_csv(CUSTOMERS_PATH)
            if preview.empty or "customer_id" not in preview.columns:
                should_rebuild = True
        except EmptyDataError:
            should_rebuild = True

    if should_rebuild:
        pd.DataFrame(CUSTOMERS).to_csv(CUSTOMERS_PATH, index=False)


def load_customers() -> pd.DataFrame:
    ensure_sample_data()
    return pd.read_csv(CUSTOMERS_PATH)
