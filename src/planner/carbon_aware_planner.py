"""
برنامه‌ریز تولید آگاه از کربن برای خط Corrugator.

هدف: توالی‌بندی سفارش‌ها به‌گونه‌ای که:
- تعداد راه‌اندازی سرد (تغییر دمای رول ≥ 8°C بین سفارش‌های متوالی) کمینه شود
- مجموع جریمه دیرکرد وزنی کمینه شود
- اولویت‌ها رعایت شوند
از الگوریتم حریصانه با کلید ترکیبی + جستجوی محلی (2-opt) استفاده می‌کند.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from dataclasses import dataclass, field

# جریمه تغییر دمای رول بالای آستانه (°C): سرد-استارت محسوب می‌شود
COLD_START_THRESHOLD_C = 8.0
# انرژی راه‌اندازی سرد: m3 گاز اضافی برای گرم کردن مجدد رول‌ها
COLD_START_EXTRA_GAS_M3 = 25.0
# CO2 اضافی هر راه‌اندازی سرد
COLD_START_EXTRA_CO2_KG = 25.0 * 1.96


@dataclass
class PlanResult:
    sequence: list  # لیست order_id
    total_cold_starts: int
    total_temp_delta_c: float
    total_extra_gas_m3: float
    total_extra_co2_kg: float
    total_tardiness_h: float
    makespan_h: float
    order_ids: list = field(default_factory=list)


def greedy_sequence(orders: pd.DataFrame, alpha=0.6, beta=0.3, gamma=0.1) -> list:
    """
    توالی حریصانه: کلید = α·(سختی دما) + β·(فوریت) + γ·(نزدیکی دما به قبلی).
    اول سفارش با بالاترین اولویت و نزدیک‌ترین دما به رول فعلی انتخاب می‌شود.
    """
    df = orders.copy().reset_index(drop=True)
    # امتیاز فوریت: اولویت بالاتر = باید زودتر
    df["urgency"] = df["priority"].astype(float)
    # نرمال‌سازی وزن
    df["w"] = df["weight_ton"].astype(float)
    # زمان شروع نسبی
    df["start_ts"] = pd.to_datetime(df["start_dt"]).astype("int64") / 1e9
    df["start_norm"] = (df["start_ts"] - df["start_ts"].min()) / (df["start_ts"].max() - df["start_ts"].min() + 1e-6)
    selected = []
    remaining = df.copy()
    current_temp = None
    while len(remaining) > 0:
        if current_temp is None:
            # اولین سفارش: اولویت بالاتر، دمای پایین‌تر (شروع گرم‌تر)
            remaining = remaining.sort_values(["priority", "target_roll_temp_c"], ascending=[False, False])
        else:
            # امتیاز هر کاندید: کمتر = بهتر
            d_temp = (remaining["target_roll_temp_c"] - current_temp).abs()
            # نرمال‌سازی
            d_temp_n = d_temp / 30.0
            score = alpha * d_temp_n - beta * (remaining["urgency"] / 3.0) - gamma * remaining["start_norm"]
            remaining = remaining.assign(_score=score).sort_values("_score")
        nxt = remaining.iloc[0]
        selected.append(nxt["order_id"])
        current_temp = nxt["target_roll_temp_c"]
        remaining = remaining.iloc[1:].copy()
    return selected


def evaluate_sequence(seq_ids: list, orders: pd.DataFrame) -> PlanResult:
    df = orders.set_index("order_id").loc[seq_ids].reset_index()
    cold_starts = 0
    temp_deltas = 0.0
    prev_temp = None
    for _, r in df.iterrows():
        if prev_temp is None:
            prev_temp = r["target_roll_temp_c"]
            continue
        d = abs(r["target_roll_temp_c"] - prev_temp)
        temp_deltas += d
        if d >= COLD_START_THRESHOLD_C:
            cold_starts += 1
        prev_temp = r["target_roll_temp_c"]
    extra_gas = cold_starts * COLD_START_EXTRA_GAS_M3
    extra_co2 = cold_starts * COLD_START_EXTRA_CO2_KG
    # makespan و دیرکرد
    cum = 0.0
    tardiness = 0.0
    for _, r in df.iterrows():
        cum += float(r["est_production_hours"])
        due = pd.to_datetime(r["due_dt"])
        # شروع تسلسلی از اولین سفارش
    # makespan کل
    makespan = float(df["est_production_hours"].sum())
    # دیرکرد تقریبی: اگر مجموع تولید > مهلت کوتاه‌ترین
    total_due_hours = (pd.to_datetime(df["due_dt"]) - pd.to_datetime(df["start_dt"])).dt.total_seconds() / 3600
    tardiness = max(0.0, float(makespan - total_due_hours.min()))
    return PlanResult(
        sequence=seq_ids,
        total_cold_starts=cold_starts,
        total_temp_delta_c=float(temp_deltas),
        total_extra_gas_m3=float(extra_gas),
        total_extra_co2_kg=float(extra_co2),
        total_tardiness_h=float(tardiness),
        makespan_h=makespan,
        order_ids=seq_ids,
    )


def two_opt_improve(seq_ids: list, orders: pd.DataFrame, max_iter=200) -> list:
    """جستجوی محلی 2-opt: اگر جابجایی دو سفارش تعداد cold-start را کم کند، اعمال می‌شود."""
    best = list(seq_ids)
    best_score = evaluate_sequence(best, orders)
    best_cost = best_score.total_cold_starts * 10 + best_score.total_temp_delta_c
    improved = True
    it = 0
    while improved and it < max_iter:
        improved = False
        it += 1
        for i in range(len(best) - 1):
            for j in range(i + 1, min(len(best), i + 6)):
                cand = best[:i] + best[i:j+1][::-1] + best[j+1:]
                cs = evaluate_sequence(cand, orders)
                cost = cs.total_cold_starts * 10 + cs.total_temp_delta_c
                if cost < best_cost - 1e-6:
                    best = cand
                    best_cost = cost
                    best_score = cs
                    improved = True
    return best


def plan_carbon_aware(orders: pd.DataFrame, alpha=0.6, beta=0.3, gamma=0.1) -> PlanResult:
    seq = greedy_sequence(orders, alpha, beta, gamma)
    seq = two_opt_improve(seq, orders)
    return evaluate_sequence(seq, orders)


def baseline_fcfs(orders: pd.DataFrame) -> PlanResult:
    """پایه: First-Come-First-Served (ترتیب start_dt)."""
    seq = orders.sort_values("start_dt")["order_id"].tolist()
    return evaluate_sequence(seq, orders)
