"""
build_datasets.py
-----------------
داده واقعی-مبنا (real-derived) و مصنوعی (synthetic) برای پروژه Inno-Kartoniran-Shasta.

منابع واقعی:
1) دیتاست UCI Combined Cycle Power Plant (CCPP) — 9568 رکورد، 6 سال (2006-2011).
   متغیرها: AT (دما)، V (خلأ اگزوز)، AP (فشار محیط)، RH (رطوبت)، PE (توان خروجی).
   ارجاع: Tüfekci (2014), Int. J. Electrical Power & Energy Systems.
2) پارامترهای واقعی صنعت کارتن از oxmaint.com / epssw.com / fibrebox.org:
   - انرژی = 12-18٪ هزینه عملیاتی (میانه 15٪)
   - بخار/دیگ = 35-45٪ کل انرژی (میانه 40٪)
   - دمای رول کاروگیتور = 165-185°C
   - دیگ‌های بیش‌اندازه معمولاً روی 40-60٪ بار
   - تله‌های بخار خراب = 3,500-8,000 دلار/سال
   - هدر حرارتی خطوط کندانس بدون عایق = 10-20٪
   - blowdown > 5٪ بدون بازیافت حرارت
   - بازار جهانی کارتن 2025 = 198.34 میلیارد دلار، CAGR 3.78٪
   - کاهش 50٪ آلاینده‌های صنعت (2006-2020)

روش: CCPP واقعی را به عنوان پایه سنسور دیگ‌بخار بگیریم و با ضرایب صنعت کارتن
به مقیاس دیگ‌بخار صنعتی (10 تن بخار/ساعت، فشار 10 bar) نگاشت می‌کنیم تا یک
داده «واقعی-مبنا» به دست آید که هم از سنسورهای واقعی نشأت می‌گیرد و هم
رفتار دیگ‌بخار کارخانه کارتن را بازتولید می‌کند. سپس داده مصنوعی بزرگ‌تر
(8760 ساعتی، 1 سال) با فرآیندهای فیزیکی واقع‌گرایانه تولید می‌شود.
"""
import os
import numpy as np
import pandas as pd

REAL_DIR = "/home/z/my-project/download/data/real"
SYN_DIR = "/home/z/my-project/download/data/synthetic"
os.makedirs(SYN_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# 1) داده واقعی-مبنا (real-derived): تبدیل CCPP به سناریوی دیگ‌بخار کارتن
# -----------------------------------------------------------------------------
ccpp = pd.read_csv(os.path.join(REAL_DIR, "ccpp_raw.csv"))
# نرمال‌سازی ستون‌ها به مقادیر فیزیکی دیگ بخار کارخانه کارتن
# AT (1.81-37.11 °C) → دمای محیط کارخانه
# V  (25-81 cm Hg) → خلأ اگزوز → تبدیل به دمای فلوی گاز خروجی دیگ (120-260°C)
# AP (992-1033 mbar) → فشار محیط
# RH (25-100%) → رطوبت نسبی
# PE (420-496 MW) → توان حرارتی → تبدیل به تولید بخار (kg/h) برای دیگ 10 t/h

AT = ccpp["AT"].values.astype(float)
V_raw = ccpp["V"].values.astype(float)
AP = ccpp["AP"].values.astype(float)
RH = ccpp["RH"].values.astype(float)
PE = ccpp["PE"].values.astype(float)

# نگاشت خطی به مقادیر دیگ‌بخار کارتن
flue_temp = 120 + (V_raw - 25) / (81 - 25) * (260 - 120)        # °C
# بار دیگ (%) = ترکیب معکوس PE و AT: بار بالاتر وقتی PE بالا و دما پایین
load_pct = 40 + (PE - PE.min()) / (PE.max() - PE.min()) * 40      # 40-80% بار
steam_flow = load_pct / 100.0 * 10000                              # kg/h (دیگ 10 t/h)
feedwater_temp = 60 + (RH - RH.min()) / (RH.max() - RH.min()) * 30  # 60-90°C
fuel_gas_flow = steam_flow * 0.075                                  # m3 gas / kg steam (پایه صنعت)
# راندمان حرارتی دیگ (%): تابع بار، دمای فلوی، تله‌های بخار
boiler_eff = (
    78.0
    + 0.12 * (load_pct - 60)                      # اثر بار (بهینه نزدیک 60-80%)
    - 0.04 * (flue_temp - 180)                    # هر 10°C فلوی بالاتر از 180 = 0.4% افت
    - 0.02 * (feedwater_temp - 75)                # اثر دمای آب تغذیه
)
boiler_eff = np.clip(boiler_eff, 70, 92)
# مصرف گاز ویژه: m3 gas / ton steam
gas_per_ton_steam = fuel_gas_flow / (steam_flow / 1000.0 + 1e-6)
# مصرف گاز ویژه: m3 gas / ton cardboard (با فرض 1.8 ton steam / ton cardboard — عدد صنعتی)
steam_per_ton_cardboard = 1.8
gas_per_ton_cardboard = gas_per_ton_steam * steam_per_ton_cardboard
# آلایندگی CO2 (kg CO2 / m3 gas ≈ 1.96)
co2_kg_per_h = fuel_gas_flow * 1.96

real_derived = pd.DataFrame({
    "timestamp": pd.date_range("2024-01-01", periods=len(ccpp), freq="h"),
    "ambient_temp_c": np.round(AT, 2),
    "ambient_pressure_mbar": np.round(AP, 1),
    "ambient_humidity_pct": np.round(RH, 1),
    "flue_gas_temp_c": np.round(flue_temp, 1),
    "feedwater_temp_c": np.round(feedwater_temp, 1),
    "boiler_load_pct": np.round(load_pct, 2),
    "steam_flow_kg_h": np.round(steam_flow, 1),
    "fuel_gas_flow_m3_h": np.round(fuel_gas_flow, 2),
    "boiler_efficiency_pct": np.round(boiler_eff, 2),
    "gas_per_ton_steam_m3": np.round(gas_per_ton_steam, 3),
    "gas_per_ton_cardboard_m3": np.round(gas_per_ton_cardboard, 3),
    "co2_emission_kg_h": np.round(co2_kg_per_h, 1),
})
real_derived.to_csv(os.path.join(REAL_DIR, "boiler_telemetry_real_derived.csv"), index=False)
print(f"[real-derived] boiler_telemetry_real_derived.csv  shape={real_derived.shape}")
print(real_derived.describe().round(2).to_string())

# -----------------------------------------------------------------------------
# 2) داده مصنوعی واقع‌گرایانه: 8760 ساعت (1 سال) تله‌متری دیگ + سفارش‌های تولید
# -----------------------------------------------------------------------------
np.random.seed(42)
N_HOURS = 8760
ts = pd.date_range("2025-01-01", periods=N_HOURS, freq="h")

# --- پروفایل بار تولید فصلی + روزانه ---
hour = ts.hour.values
month = ts.month.values
# الگوی روزانه: شیفت‌های 6-14، 14-22 فعال، 22-6 کم‌بار
daily = np.where((hour >= 6) & (hour < 22), 1.0, 0.45)
# اثر فصلی: زمستان و پاییز بار بالاتر (کاغذ کادویی)
seasonal = 1.0 + 0.25 * np.cos(2 * np.pi * (month - 1) / 12.0)
demand_factor = daily * seasonal
# نویز
demand_factor = demand_factor * np.random.normal(1.0, 0.05, N_HOURS)
demand_factor = np.clip(demand_factor, 0.3, 1.4)

# --- دیگ بخار: 10 ton/h نامی، فشار 10 bar ---
steam_flow = 4000 + demand_factor * 6000            # 4000-12400 kg/h
boiler_load = steam_flow / 10000.0 * 100            # % بار
# نوسانات دمای محیط (فصلی + روزانه)
ambient_temp = 15 + 12 * np.sin(2 * np.pi * (np.arange(N_HOURS) - 80) / 8760.0) \
               + 5 * np.sin(2 * np.pi * hour / 24.0) + np.random.normal(0, 1.5, N_HOURS)
ambient_pressure = 1013 + np.random.normal(0, 8, N_HOURS)
ambient_humidity = 55 + 25 * np.sin(2 * np.pi * (np.arange(N_HOURS) - 30) / 8760.0) \
                   + np.random.normal(0, 10, N_HOURS)
ambient_humidity = np.clip(ambient_humidity, 20, 98)

# --- پارامترهای دیگ قابل کنترل (setpoints) ---
# excess_air_pct: هوای مازاد — کم = احتراق ناقص، زیاد = هدر حرارتی
excess_air = 18 + np.random.normal(0, 3, N_HOURS)
excess_air = np.clip(excess_air, 8, 35)
# feedwater_temp: بستگی به بازیافت کندانس
feedwater_temp = 70 + np.random.normal(0, 4, N_HOURS) + (steam_flow / 10000.0 - 0.5) * 5
feedwater_temp = np.clip(feedwater_temp, 55, 92)
# blowdown_rate: نرخ دمودینگ (% جریان آب تغذیه)
blowdown_rate = 4 + np.random.normal(0, 1.2, N_HOURS)
blowdown_rate = np.clip(blowdown_rate, 1.5, 9)

# --- مدل راندمان حرارتی (فیزیکی-تجربی) ---
# راندمان نظری: 92% بار کامل، کاهش با فلوی بالا، هوای مازاد زیاد، دمودینگ زیاد
flue_gas_temp = 150 + 1.4 * (boiler_load - 50) + 2.0 * (excess_air - 18) + np.random.normal(0, 6, N_HOURS)
flue_gas_temp = np.clip(flue_gas_temp, 110, 280)

boiler_eff = (
    92.0
    - 0.05 * np.maximum(0, 60 - boiler_load)          # بار پایین
    - 0.04 * np.maximum(0, boiler_load - 85)          # بار خیلی بالا
    - 0.05 * np.maximum(0, flue_gas_temp - 180)       # فلوی بالا
    - 0.10 * np.maximum(0, excess_air - 25)           # هوای مازاد زیاد
    - 0.15 * np.maximum(0, blowdown_rate - 5)         # دمودینگ زیاد
    + 0.04 * (feedwater_temp - 75)                    # آب گرم تغذیه
)
boiler_eff = np.clip(boiler_eff + np.random.normal(0, 0.4, N_HOURS), 68, 93)

# --- مصرف سوخت ---
# انرژی مفید = steam_flow × (enthalpy蒸汽 - enthalpy water) ≈ steam × 2100 kJ/kg
# gas_flow = useful_energy / (eff × 36 MJ/m3)
gas_flow_m3_h = (steam_flow * 2100) / (boiler_eff / 100.0 * 36000)
gas_flow_m3_h = gas_flow_m3_h * np.random.normal(1.0, 0.02, N_HOURS)

# --- تولید کارتن (تقریبی: 1 ton cardboard ← 1.8 ton steam) ---
cardboard_ton_h = steam_flow / 1000.0 / 1.8
gas_per_ton_cardboard = gas_flow_m3_h / np.maximum(cardboard_ton_h, 0.1)
co2_kg_h = gas_flow_m3_h * 1.96
co2_per_ton_cardboard = gas_per_ton_cardboard * 1.96

syn_boiler = pd.DataFrame({
    "timestamp": ts,
    "ambient_temp_c": np.round(ambient_temp, 2),
    "ambient_pressure_mbar": np.round(ambient_pressure, 1),
    "ambient_humidity_pct": np.round(ambient_humidity, 1),
    "boiler_load_pct": np.round(boiler_load, 2),
    "steam_flow_kg_h": np.round(steam_flow, 1),
    "flue_gas_temp_c": np.round(flue_gas_temp, 1),
    "excess_air_pct": np.round(excess_air, 2),
    "feedwater_temp_c": np.round(feedwater_temp, 1),
    "blowdown_rate_pct": np.round(blowdown_rate, 2),
    "boiler_efficiency_pct": np.round(boiler_eff, 2),
    "fuel_gas_flow_m3_h": np.round(gas_flow_m3_h, 2),
    "cardboard_ton_h": np.round(cardboard_ton_h, 3),
    "gas_per_ton_cardboard_m3": np.round(gas_per_ton_cardboard, 3),
    "co2_emission_kg_h": np.round(co2_kg_h, 1),
    "co2_per_ton_cardboard_kg": np.round(co2_per_ton_cardboard, 2),
})
syn_boiler.to_csv(os.path.join(SYN_DIR, "boiler_telemetry_synthetic.csv"), index=False)
print(f"\n[synthetic] boiler_telemetry_synthetic.csv  shape={syn_boiler.shape}")
print(syn_boiler.describe().round(2).to_string())

# -----------------------------------------------------------------------------
# 3) سفارش‌های تولید کارتن (Corrugator production orders)
# -----------------------------------------------------------------------------
np.random.seed(7)
N_ORDERS = 480
order_ids = [f"ORD-{1000+i:04d}" for i in range(N_ORDERS)]
# نوع فلوت: A/B/C/E/BC — هر کدام دمای رول متفاوت
flute_types = ["A", "B", "C", "E", "BC"]
# دمای رول هدف (°C) — بازه 165-185°C صنعت
flute_target_temp = {"A": 175, "B": 170, "C": 172, "E": 165, "BC": 185}
flute = np.random.choice(flute_types, N_ORDERS, p=[0.2, 0.3, 0.25, 0.15, 0.10])
target_temp = np.array([flute_target_temp[f] for f in flute])
# کاغذ سطح: K (کرافت)، T (تست)، W (سفید)
liner = np.random.choice(["K", "T", "W"], N_ORDERS, p=[0.5, 0.35, 0.15])
# ابعاد ورق (متر)
width = np.random.choice([1.6, 1.8, 2.0, 2.2, 2.5], N_ORDERS)
length_m = np.random.uniform(0.6, 3.5, N_ORDERS)
# تعداد ورق
qty_sheets = np.random.randint(500, 15000, N_ORDERS)
# مساحت (m²) و وزن (تن کارتن)
area_m2 = width * length_m * qty_sheets
# وزن پایه kg/m²: کرافت 0.300، تست 0.280، سفید 0.320 — با فلوت ضریب
base_wt = {"K": 0.300, "T": 0.280, "W": 0.320}
flute_mult = {"A": 1.10, "B": 1.05, "C": 1.08, "E": 1.00, "BC": 1.18}
wt_kg = np.array([base_wt[l] * flute_mult[f] for l, f in zip(liner, flute)]) * area_m2
weight_ton = wt_kg / 1000.0
# اولویت: 1=عادی، 2=فوری، 3=بحرانی
priority = np.random.choice([1, 2, 3], N_ORDERS, p=[0.6, 0.3, 0.1])
# مهلت تحویل (روز)
due_offset = np.random.choice([1, 2, 3, 5, 7, 10], N_ORDERS)
# زمان‌های تقاضا (توزیع در سال)
start_hour = np.random.choice(N_HOURS - 72, N_ORDERS)
start_ts = [ts[h] for h in start_hour]
due_ts = [ts[h] + pd.Timedelta(days=int(d)) for h, d in zip(start_hour, due_offset)]
# زمان تولید تخمینی (ساعت): وزن / 4 ton/h میانگین
est_prod_hours = weight_ton / 4.0 + 0.3  # +0.3h برای تغییر بست

orders = pd.DataFrame({
    "order_id": order_ids,
    "flute_type": flute,
    "liner_type": liner,
    "target_roll_temp_c": target_temp,
    "width_m": width,
    "length_m": np.round(length_m, 2),
    "qty_sheets": qty_sheets,
    "area_m2": np.round(area_m2, 1),
    "weight_ton": np.round(weight_ton, 3),
    "priority": priority,
    "start_dt": start_ts,
    "due_dt": due_ts,
    "est_production_hours": np.round(est_prod_hours, 2),
})
orders = orders.sort_values("start_dt").reset_index(drop=True)
orders.to_csv(os.path.join(SYN_DIR, "production_orders_synthetic.csv"), index=False)
print(f"\n[synthetic] production_orders_synthetic.csv  shape={orders.shape}")
print(orders.head(5).to_string())
print("\nflute distribution:\n", orders["flute_type"].value_counts().to_string())

# --- فایل مانیفست / منابع ---
manifest = {
    "real_derived": {
        "boiler_telemetry_real_derived.csv": "تبدیل CCPP (UCI، 9568 رکورد) به سناریوی دیگ‌بخار کارتن",
        "ccpp_raw.csv": "داده خام UCI CCPP (منبع اصلی)",
        "sources": [
            "https://archive.ics.uci.edu/ml/datasets/Combined+Cycle+Power+Plant",
            "https://oxmaint.com/industries/delivery-operations-management/box-plant-energy-efficiency-improvement-guide",
            "https://epssw.com/blog/effective-steam-consumption-in-corrugated-manufacturing",
        ],
    },
    "synthetic": {
        "boiler_telemetry_synthetic.csv": "8760 ساعت تله‌متری دیگ (1 سال) با مدل فیزیکی-تجربی",
        "production_orders_synthetic.csv": "480 سفارش تولید Corrugator با فلوت/لاینر/اولویت/مهلت",
    },
    "industry_params": {
        "energy_pct_of_opex": "12-18٪ (میانه 15٪)",
        "steam_boiler_pct_of_energy": "35-45٪ (میانه 40٪)",
        "roll_temp_c": "165-185",
        "oversized_boiler_load": "40-60٪",
        "failed_steam_trap_cost_usd_yr": "3500-8000",
        "uninsulated_condensate_loss_pct": "10-20",
        "blowdown_no_recovery_threshold_pct": 5,
        "steam_per_ton_cardboard": 1.8,
        "co2_kg_per_m3_gas": 1.96,
        "gas_heating_value_mj_m3": 36.0,
    },
}
import json
with open(os.path.join(SYN_DIR, "_manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print("\n[manifest] saved.")
print("DONE")
