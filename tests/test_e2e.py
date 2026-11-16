"""تست‌های یکپارچه (end-to-end) پایپ‌لاین."""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_models_exist():
    mp = ROOT / "models"
    assert (mp / "efficiency_synthetic_best.joblib").exists()
    assert (mp / "gas_synthetic_best.joblib").exists()
    assert (mp / "efficiency_real_best.joblib").exists()
    assert (mp / "gas_real_best.joblib").exists()
    assert (mp / "training_report.json").exists()


def test_training_report_content():
    r = json.load(open(ROOT / "models" / "training_report.json"))
    assert "synthetic" in r and "real_derived" in r
    for src in ["synthetic","real_derived"]:
        assert "efficiency" in r[src] and "gas" in r[src]
        assert "best" in r[src]["efficiency"]
        assert "metrics" in r[src]["efficiency"]
        # حداقل یک مدل R2 قابل قبول
        best_r2 = max(v["R2"] for v in r[src]["efficiency"]["metrics"].values())
        assert best_r2 > 0.3


def test_outputs_exist():
    out = ROOT / "data" / "outputs"
    assert (out / "optimizer_savings.json").exists()
    assert (out / "optimizer_setpoints.csv").exists()
    assert (out / "planner_report.json").exists()
    assert (out / "optimal_sequence.csv").exists()


def test_optimizer_savings_positive():
    sav = json.load(open(ROOT / "data" / "outputs" / "optimizer_savings.json"))
    assert sav["efficiency_after_pct"] > sav["efficiency_before_pct"]
    assert sav["gas_saved_pct"] > 0
    assert sav["annual_gas_saved_m3"] > 0
    assert sav["annual_co2_saved_kg"] > 0


def test_planner_report_reduction():
    p = json.load(open(ROOT / "data" / "outputs" / "planner_report.json"))
    assert p["reduction"]["cold_starts"] > 0
    assert p["reduction"]["cold_starts_pct"] > 50
    assert p["reduction"]["gas_m3"] > 0
    assert p["reduction"]["co2_kg"] > 0


def test_dashboard_exists():
    assert (ROOT / "ai_dashboard.html").exists()
    html = (ROOT / "ai_dashboard.html").read_text(encoding="utf-8")
    assert "Inno-Kartoniran-Shasta" in html
    assert "Chart.js" in html or "chart.js" in html
    assert len(html) > 5000  # غیر خالی


def test_data_files_exist():
    d = ROOT / "data"
    assert (d / "real" / "ccpp_raw.csv").exists()
    assert (d / "real" / "boiler_telemetry_real_derived.csv").exists()
    assert (d / "synthetic" / "boiler_telemetry_synthetic.csv").exists()
    assert (d / "synthetic" / "production_orders_synthetic.csv").exists()
