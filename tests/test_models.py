"""تست‌های مدل‌های رگرسیون."""
import pandas as pd
import numpy as np
from pathlib import Path
from src.models.regression import train_efficiency_models, train_gas_models, _metrics
from src.utils import load_boiler_synthetic, BOILER_FEATURES


def test_metrics_function():
    y_true = np.array([1.0, 2.0, 3.0, 4.0])
    y_pred = np.array([1.1, 1.9, 3.2, 3.8])
    m = _metrics(y_true, y_pred)
    assert "MAE" in m and "RMSE" in m and "R2" in m and "MAPE_pct" in m
    assert m["R2"] > 0.9  # پیش‌بینی نزدیک
    assert m["MAE"] > 0


def test_train_efficiency_models_synthetic():
    df = load_boiler_synthetic()
    # نمونه کوچک برای سرعت تست
    df_small = df.sample(500, random_state=42)
    fitted, results, feats, best = train_efficiency_models(df_small, BOILER_FEATURES, "test")
    assert best[0] in ["LinearRegression","Ridge","RandomForest","GradientBoosting"]
    assert best[1]["R2"] > 0.5, f"R2 too low: {best[1]['R2']}"
    assert "MAE" in best[1]
    assert len(fitted) == 4


def test_train_gas_models_synthetic():
    df = load_boiler_synthetic().sample(500, random_state=42)
    fitted, results, feats, best = train_gas_models(df, BOILER_FEATURES, "test")
    assert best[0] in ["LinearRegression","Ridge","RandomForest","GradientBoosting"]
    assert "RMSE" in best[1]
    assert len(fitted) == 4
