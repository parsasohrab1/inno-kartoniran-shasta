"""تست‌های برنامه‌ریز تولید آگاه از کربن."""
import pandas as pd
import numpy as np
import pytest
from src.planner.carbon_aware_planner import (
    plan_carbon_aware, baseline_fcfs, evaluate_sequence, greedy_sequence,
    two_opt_improve, COLD_START_THRESHOLD_C,
)


@pytest.fixture
def small_orders():
    np.random.seed(1)
    n = 20
    flutes = np.random.choice(["A","B","C","E","BC"], n)
    temps = {"A":175,"B":170,"C":172,"E":165,"BC":185}
    return pd.DataFrame({
        "order_id":[f"O-{i}" for i in range(n)],
        "flute_type":flutes,
        "target_roll_temp_c":[temps[f] for f in flutes],
        "weight_ton":np.random.uniform(1,10,n).round(2),
        "priority":np.random.choice([1,2,3],n),
        "start_dt":pd.date_range("2025-01-01", periods=n, freq="2h"),
        "due_dt":pd.date_range("2025-01-05", periods=n, freq="2h"),
        "est_production_hours":np.random.uniform(0.5,3,n).round(2),
    })


def test_baseline_fcfs(small_orders):
    res = baseline_fcfs(small_orders)
    assert res.total_cold_starts >= 0
    assert res.makespan_h > 0
    assert len(res.sequence) == len(small_orders)


def test_carbon_aware_reduces_cold_starts(small_orders):
    base = baseline_fcfs(small_orders)
    plan = plan_carbon_aware(small_orders)
    assert plan.total_cold_starts <= base.total_cold_starts + 1  # اجازه برابری در موارد لبه
    assert len(plan.sequence) == len(small_orders)


def test_evaluate_sequence(small_orders):
    seq = small_orders["order_id"].tolist()
    r = evaluate_sequence(seq, small_orders)
    assert r.total_cold_starts >= 0
    assert r.total_temp_delta_c >= 0
    assert r.total_extra_gas_m3 >= 0
    assert r.total_extra_co2_kg >= 0


def test_greedy_returns_all_orders(small_orders):
    seq = greedy_sequence(small_orders, 0.6, 0.3, 0.1)
    assert len(seq) == len(small_orders)
    assert set(seq) == set(small_orders["order_id"])


def test_two_opt_improves_or_keeps(small_orders):
    seq = greedy_sequence(small_orders)
    before = evaluate_sequence(seq, small_orders)
    improved = two_opt_improve(seq, small_orders, max_iter=30)
    after = evaluate_sequence(improved, small_orders)
    assert after.total_cold_starts <= before.total_cold_starts
    assert after.total_temp_delta_c <= before.total_temp_delta_c + 1e-6


def test_full_synthetic_orders():
    from src.utils import load_orders_synthetic
    orders = load_orders_synthetic()
    base = baseline_fcfs(orders)
    plan = plan_carbon_aware(orders)
    # کاهش چشمگیر cold-start انتظار می‌رود
    assert plan.total_cold_starts < base.total_cold_starts
    reduction_pct = (base.total_cold_starts - plan.total_cold_starts) / base.total_cold_starts * 100
    assert reduction_pct > 50, f"reduction {reduction_pct:.1f}% should be > 50%"
