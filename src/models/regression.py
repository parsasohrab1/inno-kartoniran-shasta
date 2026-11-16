"""مدل‌های رگرسیون برای پیش‌بینی راندمان حرارتی و مصرف گاز ویژه."""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from src.utils import (
    load_boiler_synthetic,
    load_boiler_real_derived,
    get_features_target,
    BOILER_FEATURES,
    REAL_FEATURES,
    EFFICIENCY_TARGET,
    GAS_TARGET,
)

MODELS_DIR = Path(__file__).resolve().parents[2] / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def _metrics(y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = r2_score(y_true, y_pred)
    mape = float(np.mean(np.abs((y_true - y_pred) / np.maximum(np.abs(y_true), 1e-6))) * 100)
    return {"MAE": float(mae), "RMSE": rmse, "R2": float(r2), "MAPE_pct": mape}


def train_efficiency_models(df, features, tag="synthetic"):
    X, y, feats = get_features_target(df, features, EFFICIENCY_TARGET, add_time=("timestamp" in df.columns))
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    candidates = {
        "LinearRegression": Pipeline([("sc", StandardScaler()), ("m", LinearRegression())]),
        "Ridge": Pipeline([("sc", StandardScaler()), ("m", Ridge(alpha=1.0))]),
        "RandomForest": RandomForestRegressor(n_estimators=200, max_depth=12, random_state=42, n_jobs=-1),
        "GradientBoosting": GradientBoostingRegressor(n_estimators=300, max_depth=4, learning_rate=0.05, random_state=42),
    }
    results = {}
    fitted = {}
    for name, model in candidates.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        m = _metrics(y_test.values, preds)
        cv = cross_val_score(model, X, y, cv=5, scoring="r2", n_jobs=-1)
        m["CV_R2_mean"] = float(cv.mean())
        m["CV_R2_std"] = float(cv.std())
        results[name] = m
        fitted[name] = model
    best_name = max(results, key=lambda k: results[k]["R2"])
    return fitted, results, feats, (best_name, results[best_name])


def train_gas_models(df, features, tag="synthetic"):
    X, y, feats = get_features_target(df, features, GAS_TARGET, add_time=("timestamp" in df.columns))
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    candidates = {
        "LinearRegression": Pipeline([("sc", StandardScaler()), ("m", LinearRegression())]),
        "Ridge": Pipeline([("sc", StandardScaler()), ("m", Ridge(alpha=1.0))]),
        "RandomForest": RandomForestRegressor(n_estimators=200, max_depth=12, random_state=42, n_jobs=-1),
        "GradientBoosting": GradientBoostingRegressor(n_estimators=300, max_depth=4, learning_rate=0.05, random_state=42),
    }
    results = {}
    fitted = {}
    for name, model in candidates.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        m = _metrics(y_test.values, preds)
        cv = cross_val_score(model, X, y, cv=5, scoring="r2", n_jobs=-1)
        m["CV_R2_mean"] = float(cv.mean())
        m["CV_R2_std"] = float(cv.std())
        results[name] = m
        fitted[name] = model
    best_name = max(results, key=lambda k: results[k]["R2"])
    return fitted, results, feats, (best_name, results[best_name])


def run_all():
    import joblib
    report = {"synthetic": {}, "real_derived": {}}

    # ----- مصنوعی -----
    df = load_boiler_synthetic()
    print("\n=== مصنوعی: پیش‌بینی راندمان دیگ ===")
    fitted, results, feats, best = train_efficiency_models(df, BOILER_FEATURES, "synthetic")
    for k, v in results.items():
        print(f"  {k:20s}  R2={v['R2']:.4f}  MAE={v['MAE']:.3f}  RMSE={v['RMSE']:.3f}  CV_R2={v['CV_R2_mean']:.4f}±{v['CV_R2_std']:.4f}")
    print(f"  >> بهترین مدل: {best[0]} (R2={best[1]['R2']:.4f})")
    joblib.dump(fitted[best[0]], MODELS_DIR / "efficiency_synthetic_best.joblib")
    report["synthetic"]["efficiency"] = {"best": best[0], "metrics": results, "features": feats}

    print("\n=== مصنوعی: پیش‌بینی مصرف گاز ویژه (m3/ton کارتن) ===")
    fitted_g, results_g, feats_g, best_g = train_gas_models(df, BOILER_FEATURES, "synthetic")
    for k, v in results_g.items():
        print(f"  {k:20s}  R2={v['R2']:.4f}  MAE={v['MAE']:.3f}  RMSE={v['RMSE']:.3f}  CV_R2={v['CV_R2_mean']:.4f}±{v['CV_R2_std']:.4f}")
    print(f"  >> بهترین مدل: {best_g[0]} (R2={best_g[1]['R2']:.4f})")
    joblib.dump(fitted_g[best_g[0]], MODELS_DIR / "gas_synthetic_best.joblib")
    report["synthetic"]["gas"] = {"best": best_g[0], "metrics": results_g, "features": feats_g}

    # ----- واقعی-مبنا -----
    df_r = load_boiler_real_derived()
    print("\n=== واقعی-مبنا: پیش‌بینی راندمان دیگ ===")
    fitted_r, results_r, feats_r, best_r = train_efficiency_models(df_r, REAL_FEATURES, "real")
    for k, v in results_r.items():
        print(f"  {k:20s}  R2={v['R2']:.4f}  MAE={v['MAE']:.3f}  RMSE={v['RMSE']:.3f}  CV_R2={v['CV_R2_mean']:.4f}±{v['CV_R2_std']:.4f}")
    print(f"  >> بهترین مدل: {best_r[0]} (R2={best_r[1]['R2']:.4f})")
    joblib.dump(fitted_r[best_r[0]], MODELS_DIR / "efficiency_real_best.joblib")
    report["real_derived"]["efficiency"] = {"best": best_r[0], "metrics": results_r, "features": feats_r}

    print("\n=== واقعی-مبنا: پیش‌بینی مصرف گاز ویژه (m3/ton کارتن) ===")
    # real_derived ستون gas_per_ton_cardboard_m3 دارد
    fitted_rg, results_rg, feats_rg, best_rg = train_gas_models(df_r, REAL_FEATURES, "real")
    for k, v in results_rg.items():
        print(f"  {k:20s}  R2={v['R2']:.4f}  MAE={v['MAE']:.3f}  RMSE={v['RMSE']:.3f}  CV_R2={v['CV_R2_mean']:.4f}±{v['CV_R2_std']:.4f}")
    print(f"  >> بهترین مدل: {best_rg[0]} (R2={best_rg[1]['R2']:.4f})")
    joblib.dump(fitted_rg[best_rg[0]], MODELS_DIR / "gas_real_best.joblib")
    report["real_derived"]["gas"] = {"best": best_rg[0], "metrics": results_rg, "features": feats_rg}

    # ذخیره گزارش
    with open(MODELS_DIR / "training_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nگزارش در {MODELS_DIR / 'training_report.json'} ذخیره شد.")
    return report


if __name__ == "__main__":
    run_all()
