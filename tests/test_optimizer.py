"""تست‌های بهینه‌ساز setpoint دیگ‌بخار."""
import numpy as np
import pandas as pd
import pytest
from src.optimizer.boiler_optimizer import BoilerOptimizer, BOUNDS, MAX_FLUE_TEMP, estimate_savings


@pytest.fixture(scope="module")
def optimizer():
    from pathlib import Path
    mp = Path(__file__).resolve().parents[1] / "models" / "efficiency_synthetic_best.joblib"
    if not mp.exists():
        pytest.skip("model file not found — run pipeline first")
    return BoilerOptimizer(model_path=mp)


def test_optimizer_returns_valid_setpoints(optimizer):
    amb = (15.0, 1013.0, 55.0)
    res = optimizer.optimize(amb, load=85.0, steam_flow=8500.0, hour=10, dow=2, month=7)
    assert "excess_air_pct" in res
    assert "feedwater_temp_c" in res
    assert "blowdown_rate_pct" in res
    assert "predicted_efficiency_pct" in res
    # setpointها در محدوده مجاز
    assert BOUNDS["excess_air_pct"][0] <= res["excess_air_pct"] <= BOUNDS["excess_air_pct"][1]
    assert BOUNDS["feedwater_temp_c"][0] <= res["feedwater_temp_c"] <= BOUNDS["feedwater_temp_c"][1]
    assert BOUNDS["blowdown_rate_pct"][0] <= res["blowdown_rate_pct"] <= BOUNDS["blowdown_rate_pct"][1]
    # راندمان معقول
    assert 70 <= res["predicted_efficiency_pct"] <= 95


def test_optimizer_improves_efficiency(optimizer):
    amb = (15.0, 1013.0, 55.0)
    # setpoint بد: هوای مازاد زیاد، آب سرد، دمودینگ زیاد
    bad = optimizer.predict_efficiency(amb, 85, 8500, 10, 2, 7, 28, 60, 7)
    # setpoint بهینه
    opt = optimizer.optimize(amb, 85, 8500, 10, 2, 7)
    assert opt["predicted_efficiency_pct"] >= bad, \
        f"opt {opt['predicted_efficiency_pct']} should >= bad {bad}"


def test_estimate_savings():
    # داده مصنوعی قبل/بعد
    before = pd.DataFrame({
        "boiler_efficiency_pct":[85.0, 86.0, 87.0],
        "fuel_gas_flow_m3_h":[600,610,620],
        "cardboard_ton_h":[5.0, 5.1, 5.2],
    })
    after = before.copy()
    after["boiler_efficiency_pct"] = [88.0, 89.0, 90.0]
    sav = estimate_savings(before, after)
    assert sav["efficiency_after_pct"] > sav["efficiency_before_pct"]
    assert sav["gas_saved_m3_h"] > 0
    assert sav["annual_gas_saved_m3"] > 0
    assert sav["annual_co2_saved_kg"] > 0
