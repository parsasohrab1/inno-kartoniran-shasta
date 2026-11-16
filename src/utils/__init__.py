"""توابع کمکی: بارگذاری، پیش‌پردازش و مهندسی ویژگی."""
from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

BOILER_FEATURES = [
    "ambient_temp_c",
    "ambient_pressure_mbar",
    "ambient_humidity_pct",
    "boiler_load_pct",
    "steam_flow_kg_h",
    "flue_gas_temp_c",
    "excess_air_pct",
    "feedwater_temp_c",
    "blowdown_rate_pct",
]
REAL_FEATURES = [
    "ambient_temp_c",
    "ambient_pressure_mbar",
    "ambient_humidity_pct",
    "flue_gas_temp_c",
    "feedwater_temp_c",
    "boiler_load_pct",
    "steam_flow_kg_h",
]
EFFICIENCY_TARGET = "boiler_efficiency_pct"
GAS_TARGET = "gas_per_ton_cardboard_m3"


def load_boiler_synthetic() -> pd.DataFrame:
    p = DATA_DIR / "synthetic" / "boiler_telemetry_synthetic.csv"
    df = pd.read_csv(p, parse_dates=["timestamp"])
    return df


def load_boiler_real_derived() -> pd.DataFrame:
    p = DATA_DIR / "real" / "boiler_telemetry_real_derived.csv"
    df = pd.read_csv(p, parse_dates=["timestamp"])
    return df


def load_orders_synthetic() -> pd.DataFrame:
    p = DATA_DIR / "synthetic" / "production_orders_synthetic.csv"
    df = pd.read_csv(p, parse_dates=["start_dt", "due_dt"])
    return df


def add_time_features(df: pd.DataFrame, col: str = "timestamp") -> pd.DataFrame:
    df = df.copy()
    t = pd.to_datetime(df[col])
    df["hour"] = t.dt.hour
    df["day_of_week"] = t.dt.dayofweek
    df["month"] = t.dt.month
    df["is_daytime"] = ((df["hour"] >= 6) & (df["hour"] < 22)).astype(int)
    df["sin_hour"] = np.sin(2 * np.pi * df["hour"] / 24.0)
    df["cos_hour"] = np.cos(2 * np.pi * df["hour"] / 24.0)
    df["sin_month"] = np.sin(2 * np.pi * df["month"] / 12.0)
    df["cos_month"] = np.cos(2 * np.pi * df["month"] / 12.0)
    return df


def get_features_target(
    df: pd.DataFrame,
    features: list[str],
    target: str,
    add_time: bool = True,
):
    if add_time and "timestamp" in df.columns:
        df = add_time_features(df, "timestamp")
        feats = features + ["hour", "day_of_week", "month", "is_daytime",
                            "sin_hour", "cos_hour", "sin_month", "cos_month"]
    else:
        feats = list(features)
    X = df[feats].copy()
    y = df[target].copy() if target in df.columns else None
    return X, y, feats
