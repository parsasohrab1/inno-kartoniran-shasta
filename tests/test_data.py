"""تست‌های واحد برای پیش‌پردازش و بارگذاری داده."""
import pandas as pd
import numpy as np
from src.utils import (
    load_boiler_synthetic, load_boiler_real_derived, load_orders_synthetic,
    add_time_features, get_features_target, BOILER_FEATURES, REAL_FEATURES,
)


def test_load_boiler_synthetic():
    df = load_boiler_synthetic()
    assert df.shape[0] == 8760, f"expected 8760 rows, got {df.shape[0]}"
    for col in ["timestamp", "boiler_load_pct", "steam_flow_kg_h", "boiler_efficiency_pct",
                "fuel_gas_flow_m3_h", "gas_per_ton_cardboard_m3"]:
        assert col in df.columns, f"missing {col}"
    # بازه‌های فیزیکی معقول
    assert df["boiler_efficiency_pct"].between(60, 95).all()
    assert (df["fuel_gas_flow_m3_h"] > 0).all()
    assert (df["gas_per_ton_cardboard_m3"] > 0).all()


def test_load_boiler_real_derived():
    df = load_boiler_real_derived()
    assert df.shape[0] == 9568, f"expected 9568 rows, got {df.shape[0]}"
    assert df["boiler_efficiency_pct"].between(70, 92).all()
    assert (df["gas_per_ton_cardboard_m3"] > 0).all()


def test_load_orders_synthetic():
    df = load_orders_synthetic()
    assert df.shape[0] == 480
    for col in ["order_id", "flute_type", "target_roll_temp_c", "priority", "weight_ton"]:
        assert col in df.columns
    # فلوت‌ها در بازه صحیح
    assert set(df["flute_type"].unique()).issubset({"A","B","C","E","BC"})
    # دمای رول در بازه صنعت 165-185°C
    assert df["target_roll_temp_c"].between(165, 185).all()
    # اولویت‌ها 1-3
    assert df["priority"].between(1,3).all()


def test_add_time_features():
    df = load_boiler_synthetic().head(100)
    df2 = add_time_features(df)
    for col in ["hour","day_of_week","month","is_daytime","sin_hour","cos_hour","sin_month","cos_month"]:
        assert col in df2.columns
    assert df2["hour"].between(0,23).all()
    assert df2["is_daytime"].isin([0,1]).all()


def test_get_features_target():
    df = load_boiler_synthetic().head(500)
    X, y, feats = get_features_target(df, BOILER_FEATURES, "boiler_efficiency_pct")
    assert y is not None
    assert len(feats) == len(BOILER_FEATURES) + 8  # 8 time features
    assert X.shape[0] == 500
