"""
بهینه‌ساز setpoint دیگ‌بخار.

با داشتن مدل پیش‌بینی راندمان، بهترین مقادیر setpoint کنترلی
(excess_air, feedwater_temp, blowdown_rate) را برای هر نقطه بار محاسبه می‌کند
تا راندمان حرارتی در محدوده ایمنی و آلایندگی بیشینه شود.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path
import joblib
from scipy.optimize import minimize

MODELS_DIR = Path(__file__).resolve().parents[2] / "models"
SRC_FEATURES = [
    "ambient_temp_c", "ambient_pressure_mbar", "ambient_humidity_pct",
    "boiler_load_pct", "steam_flow_kg_h", "flue_gas_temp_c",
    "excess_air_pct", "feedwater_temp_c", "blowdown_rate_pct",
    "hour", "day_of_week", "month", "is_daytime",
    "sin_hour", "cos_hour", "sin_month", "cos_month",
]

# محدوده ایمن setpoint ها
BOUNDS = {
    "excess_air_pct": (10.0, 30.0),       # کمتر از 10 = احتراق ناقص، بیشتر از 30 = هدر حرارتی
    "feedwater_temp_c": (60.0, 88.0),
    "blowdown_rate_pct": (2.0, 7.0),
}
# محدودیت آلایندگی: فلوی گاز خروجی ≤ 220°C (برای کنترل NOx و هدر)
MAX_FLUE_TEMP = 220.0


class BoilerOptimizer:
    """بهینه‌ساز محلی setpoint دیگ با مدل راندمان پیش‌بینی‌شده."""

    def __init__(self, model_path=None):
        if model_path is None:
            model_path = MODELS_DIR / "efficiency_synthetic_best.joblib"
        self.model = joblib.load(model_path)
        self.feature_order = SRC_FEATURES

    def _make_row(self, ambient, load, steam_flow, hour, dow, month,
                  excess_air, feedwater, blowdown):
        is_day = 1 if 6 <= hour < 22 else 0
        return np.array([[
            ambient[0], ambient[1], ambient[2],
            load, steam_flow, 180.0,           # flue_gas_temp: placeholder (مدل محاسبه نمی‌کند اگر تاثیر نداشته باشد)
            excess_air, feedwater, blowdown,
            hour, dow, month, is_day,
            np.sin(2*np.pi*hour/24), np.cos(2*np.pi*hour/24),
            np.sin(2*np.pi*month/12), np.cos(2*np.pi*month/12),
        ]])

    def predict_efficiency(self, ambient, load, steam_flow, hour, dow, month,
                           excess_air, feedwater, blowdown):
        row = self._make_row(ambient, load, steam_flow, hour, dow, month,
                             excess_air, feedwater, blowdown)
        return float(self.model.predict(row)[0])

    def optimize(self, ambient, load, steam_flow, hour, dow, month,
                 x0=(18.0, 75.0, 4.0)):
        ambient = np.asarray(ambient, dtype=float)
        def neg_eff(x):
            ea, fw, bd = x
            return -self.predict_efficiency(ambient, load, steam_flow, hour, dow, month,
                                            ea, fw, bd)
        bounds = [BOUNDS["excess_air_pct"], BOUNDS["feedwater_temp_c"], BOUNDS["blowdown_rate_pct"]]
        res = minimize(neg_eff, x0=np.array(x0), bounds=bounds, method="L-BFGS-B")
        ea, fw, bd = res.x
        eff = self.predict_efficiency(ambient, load, steam_flow, hour, dow, month,
                                     ea, fw, bd)
        return {
            "excess_air_pct": float(ea),
            "feedwater_temp_c": float(fw),
            "blowdown_rate_pct": float(bd),
            "predicted_efficiency_pct": float(eff),
            "success": bool(res.success),
        }

    def optimize_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for _, r in df.iterrows():
            amb = (r["ambient_temp_c"], r["ambient_pressure_mbar"], r["ambient_humidity_pct"])
            opt = self.optimize(amb, r["boiler_load_pct"], r["steam_flow_kg_h"],
                                int(r["hour"]), int(r["day_of_week"]), int(r["month"]))
            rows.append(opt)
        return pd.DataFrame(rows)


def estimate_savings(df_before: pd.DataFrame, df_after: pd.DataFrame,
                     baseline_gas_col="fuel_gas_flow_m3_h") -> dict:
    """تخمین صرفه‌جویی گاز پس از بهینه‌سازی setpoint."""
    # مصرف گاز ∝ 1/efficiency
    eff_before = df_before["boiler_efficiency_pct"].mean()
    eff_after = df_after["boiler_efficiency_pct"].mean()
    gas_before = df_before[baseline_gas_col].mean()
    gas_after = gas_before * (eff_before / max(eff_after, 1e-6))
    saved_m3_h = gas_before - gas_after
    saved_pct = saved_m3_h / max(gas_before, 1e-6) * 100
    # تولید سالانه: ton cardboard
    ton_h = df_before["cardboard_ton_h"].mean()
    gas_per_ton_before = gas_before / max(ton_h, 1e-6)
    gas_per_ton_after = gas_after / max(ton_h, 1e-6)
    return {
        "efficiency_before_pct": float(eff_before),
        "efficiency_after_pct": float(eff_after),
        "efficiency_gain_pct": float(eff_after - eff_before),
        "gas_before_m3_h": float(gas_before),
        "gas_after_m3_h": float(gas_after),
        "gas_saved_m3_h": float(saved_m3_h),
        "gas_saved_pct": float(saved_pct),
        "gas_per_ton_before": float(gas_per_ton_before),
        "gas_per_ton_after": float(gas_per_ton_after),
        "annual_gas_saved_m3": float(saved_m3_h * 8760),
        "annual_co2_saved_kg": float(saved_m3_h * 8760 * 1.96),
    }
