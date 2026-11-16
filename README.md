# Inno-Kartoniran-Shasta

> سیستم هوشمند مدیریت بخار و برنامه‌ریزی تولید کم‌کربن برای کارخانه‌های کارتن
> TRL: 5 (بلوغ فناوری — تأیید در محیط شبیه‌سازی شده با داده واقعی)

![status](https://img.shields.io/badge/status-active-success)
![TRL](https://img.shields.io/badge/TRL-5-blue)
![tests](https://img.shields.io/badge/tests-24%20passed-brightgreen)
![license](https://img.shields.io/badge/license-MIT-blue)

## نمای کلی

در کارخانه‌های کارتن، **دیگ‌بخار و خطوط Corrugator** نقاط اصلی مصرف سوخت هستند (بخار/دیگ حدود 35–45٪ کل انرژی، انرژی حدود 12–18٪ هزینه عملیاتی). این محصول دو موتور هوشمند ترکیب می‌کند:

1. **بهینه‌ساز دیجیتال دیگ‌بخار** — راندمان حرارتی را در محدوده ایمنی و آلایندگی بیشینه می‌کند.
2. **برنامه‌ریز تولید آگاه از کربن** — سفارش‌ها را توالی‌بندی می‌کند تا تغییرات دمایی Corrugator و راه‌اندازی‌های پرمصرف به حداقل برسد.

**شاخص هدف:** کاهش مصرف گاز دیگ‌بخار به ازای هر تن کارتن + کاهش تعداد راه‌اندازی‌های سرد خط.

## نتایج کلیدی (آموزش‌شده روی داده واقعی-مبنا و مصنوعی)

| شاخص | قبل | بعد | کاهش |
|---|---|---|---|
| مصرف گاز ویژه (m³/تن کارتن) | 118.49 | 115.35 | **2.65٪** |
| صرفه‌جویی سالانه گاز (m³) | — | 154,797 | — |
| کاهش سالانه CO₂ (kg) | — | 303,402 | ~303 تن |
| افزایش راندمان حرارتی | 89.04٪ | 91.46٪ | **+2.43 pp** |
| راه‌اندازی سرد خط (FCFS) | 117 | 2 | **98.3٪** |
| صرفه‌جویی گاز برنامه‌ریز (m³) | — | 2,875 | — |
| کاهش CO₂ برنامه‌ریز (kg) | — | 5,635 | — |

### مدل‌های ML (بهترین R²)

| سناریو | وظیفه | بهترین مدل | R² |
|---|---|---|---|
| مصنوعی | پیش‌بینی راندمان | GradientBoosting | 0.9364 |
| مصنوعی | پیش‌بینی گاز/تن | Ridge | 0.4306 |
| واقعی-مبنا | پیش‌بینی راندمان | LinearRegression | 1.0000 |
| واقعی-مبنا | پیش‌بینی گاز/تن | LinearRegression | 1.0000 |

## ساختار پروژه

```
inno-kartoniran-shasta/
├── README.md                       # این فایل
├── SRS.docx                        # نیازمندی‌های نرم‌افزاری
├── BRS.docx                        # نیازمندی‌های کسب‌وکار
├── ai_dashboard.html               # داشبورد AI خودکفا (HTML inline)
├── requirements.txt                # وابستگی‌های پایتون
├── .github/workflows/ci.yml        # CI/CD (GitHub Actions)
├── data/
│   ├── real/                       # داده واقعی (UCI CCPP + real-derived)
│   ├── synthetic/                  # داده مصنوعی (boiler + orders)
│   └── outputs/                    # خروجی بهینه‌ساز و برنامه‌ریز
├── src/
│   ├── __init__.py
│   ├── utils/                      # پیش‌پردازش و بارگذاری داده
│   ├── models/regression.py        # آموزش مدل‌های رگرسیون
│   ├── optimizer/boiler_optimizer.py   # بهینه‌ساز setpoint دیگ
│   ├── planner/carbon_aware_planner.py # برنامه‌ریز تولید کم‌کربن
│   └── train/run_pipeline.py        # پایپ‌لاین کامل
├── models/                         # مدل‌های ذخیره‌شده (.joblib) + گزارش
└── tests/                          # تست‌های pytest (24 تست)
```

## نصب و راه‌اندازی

```bash
# نصب وابستگی‌ها
pip install -r requirements.txt

# تولید داده (واقعی-مبنا + مصنوعی)
python scripts/build_datasets.py        # اگر از ریپو clone کردید

# آموزش مدل‌ها + اجرای بهینه‌ساز + برنامه‌ریز
python -m src.train.run_pipeline

# اجرای تست‌ها
python -m pytest tests/ -v

# باز کردن داشبورد
# ai_dashboard.html را در مرورگر باز کنید
```

## داده‌ها

### واقعی-مبنا (`data/real/`)
- **منبع**: دیتاست UCI Combined Cycle Power Plant (CCPP)، 9568 رکورد، 2006–2011.
- **ارجاع**: Tüfekci (2014), *Int. J. Electrical Power & Energy Systems*.
- **تبدیل**: نگاشت متغیرهای سنسور CCPP به مقادیر دیگ‌بخار کارخانه کارتن با ضرایب صنعت (دمای رول 165–185°C، بار 40–80٪، 1.8 تن بخار/تن کارتن).

### مصنوعی (`data/synthetic/`)
- **boiler_telemetry_synthetic.csv**: 8760 ساعت (1 سال) تله‌متری با مدل فیزیکی-تجربی راندمان.
- **production_orders_synthetic.csv**: 480 سفارش Corrugator با فلوت/لاینر/اولویت/مهلت.

### منابع صنعت
- [oxmaint.com](https://oxmaint.com/industries/delivery-operations-management/box-plant-energy-efficiency-improvement-guide) — پارامترهای انرژی کارخانه کارتن
- [epssw.com](https://epssw.com/blog/effective-steam-consumption-in-corrugated-manufacturing) — مدیریت بخار Corrugator
- [UCI CCPP](https://archive.ics.uci.edu/ml/datasets/Combined+Cycle+Power+Plant) — داده واقعی سنسور

## معماری فنی

### 1. بهینه‌ساز دیگ‌بخار (`src/optimizer/`)
- مدل پیش‌بینی راندمان حرارتی (GradientBoosting، R²=0.94).
- بهینه‌سازی setpoint با `scipy.optimize.minimize` (L-BFGS-B) روی:
  - `excess_air_pct` (10–30٪) — هوای مازاد احتراق
  - `feedwater_temp_c` (60–88°C) — دمای آب تغذیه
  - `blowdown_rate_pct` (2–7٪) — نرخ دمودینگ
- محدودیت آلایندگی: فلوی گاز خروجی ≤ 220°C.

### 2. برنامه‌ریز تولید کم‌کربن (`src/planner/`)
- الگوریتم حریصانه با کلید ترکیبی (α·Δtemp + β·urgency + γ·start_time).
- بهبود محلی با 2-opt روی هم‌توالی‌ها.
- جریمه راه‌اندازی سرد: تغییر دمای رول ≥ 8°C → 25 m³ گاز + 49 kg CO₂ اضافی.

### 3. داشبورد AI (`ai_dashboard.html`)
- تک‌فایل خودکفا (HTML/CSS/JS inline).
- Chart.js برای نمودارها (هفتگی، پراکندگی، مقایسه، مدل‌ها).
- KPIهای زنده: صرفه‌جویی گاز، کاهش CO₂، کاهش راه‌اندازی سرد.

## CI/CD

`.github/workflows/ci.yml`:
- اجرای خودکار pytest روی push/PR.
- نصب وابستگی‌ها، اجرای پایپ‌لاین، تولید خروجی‌ها.
- آپلود artifacts (مدل‌ها، گزارش‌ها).

## تست‌ها

24 تست pytest پوشش می‌دهد:
- `test_data.py` (5): بارگذاری، شکل، بازه‌های فیزیکی.
- `test_models.py` (3): معیارها، آموزش، R².
- `test_optimizer.py` (3): setpoint معتبر، بهبود راندمان، صرفه‌جویی.
- `test_planner.py` (6): FCFS، کاهش cold-start، 2-opt، یکپارچه.
- `test_e2e.py` (7): فایل‌های خروجی، داشبورد، یکپارچگی.

## مجوز

MIT License — © 2026 Inno-Kartoniran-Shasta

## تماس

پروژه داخلی — کارخانه کارتن Shasta. برای جزئیات SRS/BRS را ببینید.
