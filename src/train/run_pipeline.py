"""اسکریپت آموزش مدل‌ها و اجرای بهینه‌ساز + برنامه‌ریز، و ذخیره گزارش."""
from __future__ import annotations
import json
import sys
from pathlib import Path

# اطمینان از قابل import بودن src
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.models.regression import run_all as train_all_models
from src.optimizer.boiler_optimizer import BoilerOptimizer, estimate_savings
from src.planner.carbon_aware_planner import plan_carbon_aware, baseline_fcfs
from src.utils import load_boiler_synthetic, load_orders_synthetic, add_time_features


def main():
    print("=" * 70)
    print("مرحله 1: آموزش مدل‌های ML روی داده واقعی-مبنا و مصنوعی")
    print("=" * 70)
    report = train_all_models()

    print("\n" + "=" * 70)
    print("مرحله 2: بهینه‌سازی setpoint دیگ‌بخار با مدل آموزش‌شده")
    print("=" * 70)
    df = load_boiler_synthetic()
    df = add_time_features(df)
    opt = BoilerOptimizer()
    # بهینه‌سازی روی یک نمونه 240 ساعتی (10 روز)
    sample = df.iloc[:240].copy()
    opt_df = opt.optimize_batch(sample)
    # مقایسه قبل/بعد
    df_before = sample.copy()
    df_after = sample.copy()
    df_after["boiler_efficiency_pct"] = opt_df["predicted_efficiency_pct"].values
    df_after["excess_air_pct"] = opt_df["excess_air_pct"].values
    df_after["feedwater_temp_c"] = opt_df["feedwater_temp_c"].values
    df_after["blowdown_rate_pct"] = opt_df["blowdown_rate_pct"].values
    sav = estimate_savings(df_before, df_after)
    print("\nنتایج بهینه‌سازی setpoint (نمونه 240 ساعت):")
    for k, v in sav.items():
        print(f"  {k:30s} = {v:.4f}")
    # ذخیره خروجی بهینه‌ساز
    out_dir = ROOT / "data" / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "optimizer_savings.json", "w", encoding="utf-8") as f:
        json.dump(sav, f, ensure_ascii=False, indent=2)
    opt_df.to_csv(out_dir / "optimizer_setpoints.csv", index=False)

    print("\n" + "=" * 70)
    print("مرحله 3: برنامه‌ریزی تولید آگاه از کربن (Corrugator sequencing)")
    print("=" * 70)
    orders = load_orders_synthetic()
    base = baseline_fcfs(orders)
    plan = plan_carbon_aware(orders)
    print("\nپایه (FCFS):")
    print(f"  cold_starts = {base.total_cold_starts}")
    print(f"  total_temp_delta_c = {base.total_temp_delta_c:.2f}")
    print(f"  extra_gas_m3 = {base.total_extra_gas_m3:.2f}")
    print(f"  extra_co2_kg = {base.total_extra_co2_kg:.2f}")
    print(f"  makespan_h = {base.makespan_h:.2f}")
    print("\nبرنامه آگاه از کربن:")
    print(f"  cold_starts = {plan.total_cold_starts}")
    print(f"  total_temp_delta_c = {plan.total_temp_delta_c:.2f}")
    print(f"  extra_gas_m3 = {plan.total_extra_gas_m3:.2f}")
    print(f"  extra_co2_kg = {plan.total_extra_co2_kg:.2f}")
    print(f"  makespan_h = {plan.makespan_h:.2f}")
    cold_reduction = (base.total_cold_starts - plan.total_cold_starts)
    cold_reduction_pct = cold_reduction / max(base.total_cold_starts, 1) * 100
    co2_saved = base.total_extra_co2_kg - plan.total_extra_co2_kg
    gas_saved = base.total_extra_gas_m3 - plan.total_extra_gas_m3
    print("\n>>> مقایسه:")
    print(f"  کاهش cold-start: {cold_reduction} ({cold_reduction_pct:.1f}%)")
    print(f"  صرفه‌جویی گاز: {gas_saved:.2f} m3")
    print(f"  کاهش CO2: {co2_saved:.2f} kg")
    plan_report = {
        "baseline_fcfs": base.__dict__,
        "carbon_aware": plan.__dict__,
        "reduction": {
            "cold_starts": int(cold_reduction),
            "cold_starts_pct": float(cold_reduction_pct),
            "gas_m3": float(gas_saved),
            "co2_kg": float(co2_saved),
        },
    }
    with open(out_dir / "planner_report.json", "w", encoding="utf-8") as f:
        json.dump(plan_report, f, ensure_ascii=False, indent=2, default=str)
    pd.DataFrame(plan.sequence, columns=["order_id"]).to_csv(
        out_dir / "optimal_sequence.csv", index=False)
    print(f"\nگزارش‌ها در {out_dir} ذخیره شد.")
    print("\nهمه مراحل DONE.")


if __name__ == "__main__":
    main()
