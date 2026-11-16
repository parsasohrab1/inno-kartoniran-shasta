"""استخراج داده‌های نمودار داشبورد از خروجی‌ها برای embed در HTML."""
import json, sys
from pathlib import Path
ROOT = Path("/home/z/my-project/download")
sys.path.insert(0, str(ROOT))
from src.utils import load_boiler_synthetic, load_orders_synthetic, add_time_features

out = {}
# 1) KPIهای اصلی
sav = json.load(open(ROOT/"data/outputs/optimizer_savings.json"))
plan = json.load(open(ROOT/"data/outputs/planner_report.json"))
tr = json.load(open(ROOT/"models/training_report.json"))

out["kpi"] = {
    "gas_saved_pct": sav["gas_saved_pct"],
    "annual_gas_saved_m3": sav["annual_gas_saved_m3"],
    "annual_co2_saved_kg": sav["annual_co2_saved_kg"],
    "efficiency_gain_pct": sav["efficiency_gain_pct"],
    "cold_starts_reduction_pct": plan["reduction"]["cold_starts_pct"],
    "cold_starts_before": plan["baseline_fcfs"]["total_cold_starts"],
    "cold_starts_after": plan["carbon_aware"]["total_cold_starts"],
    "planner_co2_saved_kg": plan["reduction"]["co2_kg"],
    "planner_gas_saved_m3": plan["reduction"]["gas_m3"],
    "best_model_eff_synthetic": tr["synthetic"]["efficiency"]["best"],
    "best_model_eff_synthetic_r2": tr["synthetic"]["efficiency"]["metrics"][tr["synthetic"]["efficiency"]["best"]]["R2"],
    "best_model_eff_real": tr["real_derived"]["efficiency"]["best"],
    "best_model_eff_real_r2": tr["real_derived"]["efficiency"]["metrics"][tr["real_derived"]["efficiency"]["best"]]["R2"],
}

# 2) سری زمانی هفتگی: راندمان و مصرف گاز
df = load_boiler_synthetic()
df["ts"] = df["timestamp"]
df["week"] = df["timestamp"].dt.isocalendar().week
weekly = df.groupby("week").agg(
    eff=("boiler_efficiency_pct", "mean"),
    gas=("fuel_gas_flow_m3_h", "mean"),
    gas_per_ton=("gas_per_ton_cardboard_m3", "mean"),
    co2=("co2_emission_kg_h", "mean"),
    load=("boiler_load_pct", "mean"),
).reset_index()
out["weekly"] = weekly.to_dict(orient="records")

# 3) توزیع راندمان قبل/بعد بهینه‌سازی
out["eff_distribution"] = {
    "before_mean": sav["efficiency_before_pct"],
    "after_mean": sav["efficiency_after_pct"],
}

# 4) مقایسه برنامه‌ریز: FCFS vs Carbon-aware
out["planner_compare"] = {
    "labels": ["Cold Starts", "Extra Gas (m³)", "Extra CO₂ (kg)"],
    "fcfs": [plan["baseline_fcfs"]["total_cold_starts"], plan["baseline_fcfs"]["total_extra_gas_m3"], plan["baseline_fcfs"]["total_extra_co2_kg"]],
    "carbon_aware": [plan["carbon_aware"]["total_cold_starts"], plan["carbon_aware"]["total_extra_gas_m3"], plan["carbon_aware"]["total_extra_co2_kg"]],
}

# 5) مدل‌ها: R2 هر مدل هر سناریو
out["models"] = {
    "synthetic_eff": {k: v["R2"] for k, v in tr["synthetic"]["efficiency"]["metrics"].items()},
    "synthetic_gas": {k: v["R2"] for k, v in tr["synthetic"]["gas"]["metrics"].items()},
    "real_eff": {k: v["R2"] for k, v in tr["real_derived"]["efficiency"]["metrics"].items()},
    "real_gas": {k: v["R2"] for k, v in tr["real_derived"]["gas"]["metrics"].items()},
}

# 6) پراکندگی راندمان vs بار (نمونه 500 نقطه)
sample = df.sample(min(500, len(df)), random_state=1)
out["scatter_eff_load"] = {
    "load": sample["boiler_load_pct"].round(2).tolist(),
    "eff": sample["boiler_efficiency_pct"].round(2).tolist(),
    "gas_per_ton": sample["gas_per_ton_cardboard_m3"].round(2).tolist(),
}

# 7) سفارش‌ها: تعداد به تفکیک فلوت
orders = load_orders_synthetic()
out["flute_dist"] = orders["flute_type"].value_counts().to_dict()
out["priority_dist"] = orders["priority"].value_counts().sort_index().to_dict()

# 8) توالی بهینه: 30 سفارش اول + دما
seq = json.load(open(ROOT/"data/outputs/optimal_sequence.csv_readable.json", "r")) if False else None
seq_df = orders.set_index("order_id").loc[plan["carbon_aware"]["sequence"][:30]].reset_index()
out["optimal_seq_top30"] = {
    "order_ids": seq_df["order_id"].tolist(),
    "temps": seq_df["target_roll_temp_c"].tolist(),
    "flute": seq_df["flute_type"].tolist(),
    "weight": seq_df["weight_ton"].round(2).tolist(),
    "priority": seq_df["priority"].tolist(),
}

Path(ROOT/"dashboard_data.json").write_text(json.dumps(out, ensure_ascii=False, default=str), encoding="utf-8")
print("dashboard_data.json written, size:", len(json.dumps(out)), "bytes")
print("KPI:", json.dumps(out["kpi"], ensure_ascii=False, indent=2))
