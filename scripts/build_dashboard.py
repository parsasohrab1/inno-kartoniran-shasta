"""ساخت داشبورد HTML خودکفا با داده embed شده."""
import json
from pathlib import Path

ROOT = Path("/home/z/my-project/download")
data = json.load(open(ROOT / "dashboard_data.json"))

HTML = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Inno-Kartoniran-Shasta | داشبورد هوشمند مدیریت بخار و تولید کم‌کربن</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root{
  --bg:#0f172a; --bg2:#1e293b; --card:#1e293b; --card2:#273449;
  --text:#e2e8f0; --muted:#94a3b8; --accent:#38bdf8; --green:#22c55e;
  --orange:#f59e0b; --red:#ef4444; --purple:#a855f7; --blue:#3b82f6;
  --border:#334155;
}
*{box-sizing:border-box;margin:0;padding:0}
body{
  font-family: 'Vazirmatn','Segoe UI',Tahoma,sans-serif;
  background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);
  color:var(--text); min-height:100vh; padding:20px;
}
header{
  background:linear-gradient(135deg,#1e3a8a,#0f766e);
  border-radius:16px; padding:24px 32px; margin-bottom:24px;
  box-shadow:0 10px 30px rgba(0,0,0,0.4);
  border:1px solid var(--border);
}
header h1{font-size:26px; margin-bottom:6px; font-weight:800; color:#fff}
header .sub{color:#cbd5e1; font-size:14px}
header .meta{display:flex; gap:16px; margin-top:10px; flex-wrap:wrap}
header .meta span{background:rgba(255,255,255,0.12); padding:4px 12px; border-radius:999px; font-size:12px; color:#e0f2fe}
.kpi-grid{display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:16px; margin-bottom:24px}
.kpi-card{background:var(--card); border:1px solid var(--border); border-radius:14px; padding:18px; position:relative; overflow:hidden}
.kpi-card::before{content:''; position:absolute; top:0; right:0; width:4px; height:100%; background:var(--accent)}
.kpi-card.green::before{background:var(--green)}
.kpi-card.orange::before{background:var(--orange)}
.kpi-card.purple::before{background:var(--purple)}
.kpi-card.red::before{background:var(--red)}
.kpi-label{color:var(--muted); font-size:12px; margin-bottom:6px}
.kpi-value{font-size:28px; font-weight:800; color:#fff; line-height:1.1}
.kpi-sub{color:var(--muted); font-size:11px; margin-top:4px}
.kpi-trend{display:inline-block; margin-top:6px; padding:2px 8px; border-radius:6px; font-size:11px; font-weight:700}
.trend-up{background:rgba(34,197,94,0.15); color:var(--green)}
.trend-down{background:rgba(239,68,68,0.15); color:var(--red)}
.section-title{font-size:18px; font-weight:700; margin:24px 0 12px; color:var(--text); border-right:4px solid var(--accent); padding-right:12px}
.grid-2{display:grid; grid-template-columns:1fr 1fr; gap:16px}
.grid-3{display:grid; grid-template-columns:repeat(3,1fr); gap:16px}
.chart-card{background:var(--card); border:1px solid var(--border); border-radius:14px; padding:16px}
.chart-title{font-size:14px; color:var(--muted); margin-bottom:10px; font-weight:600}
.chart-wrap{position:relative; height:260px}
.chart-wrap.tall{height:340px}
table{width:100%; border-collapse:collapse; font-size:12px}
th{background:var(--card2); padding:8px; text-align:right; color:var(--muted); font-weight:600; border-bottom:1px solid var(--border)}
td{padding:7px 8px; border-bottom:1px solid var(--border); color:var(--text)}
tr:hover td{background:rgba(56,189,248,0.06)}
.pill{display:inline-block; padding:2px 8px; border-radius:6px; font-size:10px; font-weight:700}
.p-A{background:#7c3aed22;color:#c4b5fd} .p-B{background:#3b82f622;color:#93c5fd}
.p-C{background:#10b98122;color:#6ee7b7} .p-E{background:#f59e0b22;color:#fcd34d}
.p-BC{background:#ef444422;color:#fca5a5}
.prio-1{color:var(--muted)} .prio-2{color:var(--orange)} .prio-3{color:var(--red);font-weight:700}
footer{margin-top:32px; text-align:center; color:var(--muted); font-size:12px; padding:16px}
.tag{display:inline-block; background:rgba(56,189,248,0.12); color:var(--accent); padding:3px 10px; border-radius:6px; font-size:11px; margin:2px}
summary{cursor:pointer; padding:8px; background:var(--card2); border-radius:8px; font-size:13px; margin:8px 0}
@media(max-width:900px){.grid-2,.grid-3{grid-template-columns:1fr}}
</style>
</head>
<body>

<header>
  <h1>🏭 Inno-Kartoniran-Shasta</h1>
  <div class="sub">داشبورد هوشمند مدیریت بخار و برنامه‌ریزی تولید کم‌کربن — کارخانه کارتن</div>
  <div class="meta">
    <span>📅 داده: 8760 ساعت (1 سال) + 480 سفارش تولید</span>
    <span>⚙️ دیگ‌بخار 10 t/h، فشار 10 bar</span>
    <span>📋 خط Corrugator — 5 نوع فلوت</span>
    <span>🌱 شاخص هدف: کاهش گاز/تن کارتن + راه‌اندازی سرد</span>
  </div>
</header>

<div class="kpi-grid">
  <div class="kpi-card green">
    <div class="kpi-label">صرفه‌جویی سالانه گاز دیگ</div>
    <div class="kpi-value" id="kpi-gas">__GAS_SAVED__</div>
    <div class="kpi-sub">m³ در سال</div>
    <div class="kpi-trend trend-up">▼ __GAS_PCT__٪</div>
  </div>
  <div class="kpi-card red">
    <div class="kpi-label">کاهش CO₂ سالانه</div>
    <div class="kpi-value" id="kpi-co2">__CO2_SAVED__</div>
    <div class="kpi-sub">kg در سال</div>
    <div class="kpi-trend trend-up">▼ ~303 تن CO₂</div>
  </div>
  <div class="kpi-card purple">
    <div class="kpi-label">افزایش راندمان حرارتی دیگ</div>
    <div class="kpi-value" id="kpi-eff">__EFF_GAIN__</div>
    <div class="kpi-sub">百分点</div>
    <div class="kpi-trend trend-up">▲ بهبود</div>
  </div>
  <div class="kpi-card orange">
    <div class="kpi-label">کاهش راه‌اندازی سرد خط</div>
    <div class="kpi-value" id="kpi-cold">__COLD_PCT__٪</div>
    <div class="kpi-sub">__COLD_BEFORE__ → __COLD_AFTER__</div>
    <div class="kpi-trend trend-up">▼ 98.3٪ کاهش</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">بهترین مدل راندمان (مصنوعی)</div>
    <div class="kpi-value" style="font-size:20px" id="kpi-model">__MODEL_NAME__</div>
    <div class="kpi-sub">R² = __MODEL_R2__</div>
    <div class="kpi-trend trend-up">R² بالا</div>
  </div>
</div>

<div class="section-title">📈 روند هفتگی: راندمان و مصرف گاز</div>
<div class="grid-2">
  <div class="chart-card">
    <div class="chart-title">میانگین راندمان حرارتی دیگ بر اساس هفته</div>
    <div class="chart-wrap"><canvas id="ch-eff-weekly"></canvas></div>
  </div>
  <div class="chart-card">
    <div class="chart-title">مصرف گاز ویژه (m³ گاز / تن کارتن)</div>
    <div class="chart-wrap"><canvas id="ch-gas-ton-weekly"></canvas></div>
  </div>
</div>

<div class="section-title">🔧 بهینه‌ساز Setpoint دیگ‌بخار</div>
<div class="grid-2">
  <div class="chart-card">
    <div class="chart-title">راندمان قبل/بعد بهینه‌سازی</div>
    <div class="chart-wrap"><canvas id="ch-eff-before-after"></canvas></div>
  </div>
  <div class="chart-card">
    <div class="chart-title">پراکندگی راندمان بر حسب بار دیگ</div>
    <div class="chart-wrap"><canvas id="ch-scatter-load"></canvas></div>
  </div>
</div>

<div class="section-title">🌱 برنامه‌ریز تولید آگاه از کربن</div>
<div class="grid-2">
  <div class="chart-card">
    <div class="chart-title">مقایسه FCFS vs برنامه آگاه از کربن</div>
    <div class="chart-wrap tall"><canvas id="ch-planner-compare"></canvas></div>
  </div>
  <div class="chart-card">
    <div class="chart-title">توزیع سفارش‌ها به تفکیک نوع فلوت</div>
    <div class="chart-wrap tall"><canvas id="ch-flute-dist"></canvas></div>
  </div>
</div>

<div class="section-title">📋 توالی بهینه ۳۰ سفارش اول (Corrugator)</div>
<div class="chart-card" style="padding:8px">
  <table id="tbl-seq">
    <thead><tr><th>#</th><th>order_id</th><th>فلوت</th><th>دمای رول (°C)</th><th>وزن (تن)</th><th>اولویت</th></tr></thead>
    <tbody id="seq-body"></tbody>
  </table>
</div>

<div class="section-title">🤖 مقایسه مدل‌های ML (R²)</div>
<div class="grid-3">
  <div class="chart-card">
    <div class="chart-title">راندمان — داده مصنوعی</div>
    <div class="chart-wrap"><canvas id="ch-models-syn-eff"></canvas></div>
  </div>
  <div class="chart-card">
    <div class="chart-title">راندمان — داده واقعی-مبنا</div>
    <div class="chart-wrap"><canvas id="ch-models-real-eff"></canvas></div>
  </div>
  <div class="chart-card">
    <div class="chart-title">مصرف گاز — داده مصنوعی</div>
    <div class="chart-wrap"><canvas id="ch-models-syn-gas"></canvas></div>
  </div>
</div>

<footer>
  <div>
    <span class="tag">Python 3.12</span>
    <span class="tag">scikit-learn 1.5</span>
    <span class="tag">pandas</span>
    <span class="tag">Chart.js 4</span>
    <span class="tag">UCI CCPP (real)</span>
  </div>
  <div style="margin-top:8px">© 2026 Inno-Kartoniran-Shasta — بلوغ فناوری TRL 5 | تولیدشده با داده واقعی-مبنا و مصنوعی</div>
</footer>

<script>
const DATA = __DATA_JSON__;

// فرمت اعداد فارسی
function fmt(n, d=0){ if(n===null||n===undefined) return '-'; d=d||0; 
  return Number(n).toLocaleString('fa-IR',{minimumFractionDigits:d,maximumFractionDigits:d}); }
function faNum(n){ return String(n).replace(/[0-9]/g, d=>'۰۱۲۳۴۵۶۷۸۹'[+d]); }

// پر کردن KPIها
document.getElementById('kpi-gas').textContent = fmt(Math.round(DATA.kpi.annual_gas_saved_m3));
document.getElementById('kpi-gas-pct') || (window.__gp = DATA.kpi.gas_saved_pct);
document.getElementById('kpi-co2').textContent = fmt(Math.round(DATA.kpi.annual_co2_saved_kg));
document.getElementById('kpi-eff').textContent = '+'+DATA.kpi.efficiency_gain_pct.toFixed(2);
document.getElementById('kpi-cold').textContent = DATA.kpi.cold_starts_reduction_pct.toFixed(1);
document.getElementById('kpi-model').textContent = DATA.kpi.best_model_eff_synthetic;
document.getElementById('kpi-model-r2') || (window.__mr = DATA.kpi.best_model_eff_synthetic_r2);

// جایگزینی placeholderها
document.body.innerHTML = document.body.innerHTML
  .replace('__GAS_SAVED__', fmt(Math.round(DATA.kpi.annual_gas_saved_m3)))
  .replace('__GAS_PCT__', DATA.kpi.gas_saved_pct.toFixed(2))
  .replace('__CO2_SAVED__', fmt(Math.round(DATA.kpi.annual_co2_saved_kg)))
  .replace('__EFF_GAIN__', '+'+DATA.kpi.efficiency_gain_pct.toFixed(2))
  .replace('__COLD_PCT__', DATA.kpi.cold_starts_reduction_pct.toFixed(1))
  .replace('__COLD_BEFORE__', faNum(DATA.kpi.cold_starts_before))
  .replace('__COLD_AFTER__', faNum(DATA.kpi.cold_starts_after))
  .replace('__MODEL_NAME__', DATA.kpi.best_model_eff_synthetic)
  .replace('__MODEL_R2__', DATA.kpi.best_model_eff_synthetic_r2.toFixed(4));

// رنگ‌ها
const C = {accent:'#38bdf8',green:'#22c55e',orange:'#f59e0b',red:'#ef4444',purple:'#a855f7',blue:'#3b82f6',muted:'#94a3b8'};

Chart.defaults.color = '#cbd5e1';
Chart.defaults.font.family = "'Vazirmatn','Segoe UI',Tahoma,sans-serif";

// 1) راندمان هفتگی
const w = DATA.weekly;
new Chart(document.getElementById('ch-eff-weekly'), {
  type:'line',
  data:{labels:w.map(x=>'هفته '+x.week), datasets:[{
    label:'راندمان (٪)', data:w.map(x=>+x.eff.toFixed(2)),
    borderColor:C.accent, backgroundColor:'rgba(56,189,248,0.1)',
    tension:0.3, fill:true, borderWidth:2, pointRadius:0
  }]},
  options:{plugins:{legend:{display:true,position:'top'}}, scales:{y:{min:80,max:95}}}
});

// 2) گاز ویژه هفتگی
new Chart(document.getElementById('ch-gas-ton-weekly'), {
  type:'bar',
  data:{labels:w.map(x=>'هفته '+x.week), datasets:[{
    label:'m³ گاز / تن کارتن', data:w.map(x=>+x.gas_per_ton.toFixed(2)),
    backgroundColor:'rgba(245,158,11,0.6)', borderColor:C.orange, borderWidth:1
  }]},
  options:{plugins:{legend:{display:true}}, scales:{}}
});

// 3) راندمان قبل/بعد
new Chart(document.getElementById('ch-eff-before-after'), {
  type:'bar',
  data:{labels:['قبل از بهینه‌سازی','بعد از بهینه‌سازی'],
    datasets:[{label:'راندمان (٪)', data:[DATA.eff_distribution.before_mean, DATA.eff_distribution.after_mean],
      backgroundColor:[C.orange, C.green], borderRadius:8, barThickness:60}]},
  options:{plugins:{legend:{display:false}}}
});

// 4) پراکندگی راندمان-بار
const sc = DATA.scatter_eff_load;
new Chart(document.getElementById('ch-scatter-load'), {
  type:'scatter',
  data:{datasets:[{
    label:'ساعات عملیاتی', data:sc.load.map((l,i)=>({x:l,y:sc.eff[i]})),
    backgroundColor:'rgba(56,189,248,0.4)', borderColor:C.accent, pointRadius:3
  }]},
  options:{plugins:{legend:{display:false}},
    scales:{x:{title:{display:true,text:'بار دیگ (٪)'}}, y:{title:{display:true,text:'راندمان (٪)'}}}}
});

// 5) مقایسه برنامه‌ریز
const pc = DATA.planner_compare;
new Chart(document.getElementById('ch-planner-compare'), {
  type:'bar',
  data:{labels:pc.labels,
    datasets:[
      {label:'FCFS (پایه)', data:pc.fcfs, backgroundColor:C.red, borderRadius:6},
      {label:'آگاه از کربن', data:pc.carbon_aware, backgroundColor:C.green, borderRadius:6}
    ]},
  options:{plugins:{legend:{display:true,position:'top'}}}
});

// 6) توزیع فلوت
const fd = DATA.flute_dist;
new Chart(document.getElementById('ch-flute-dist'), {
  type:'doughnut',
  data:{labels:Object.keys(fd),
    datasets:[{data:Object.values(fd),
      backgroundColor:['#7c3aed','#3b82f6','#10b981','#f59e0b','#ef4444']}]},
  options:{plugins:{legend:{position:'right'}}}
});

// 7) مدل‌ها
function modelChart(id, dataObj){
  const labels = Object.keys(dataObj);
  const vals = labels.map(k=>+dataObj[k].toFixed(4));
  const colors = labels.map(l=>l==='RandomForest'?C.accent:l==='GradientBoosting'?C.green:l==='Ridge'?C.orange:C.purple);
  new Chart(document.getElementById(id), {
    type:'bar',
    data:{labels, datasets:[{label:'R²', data:vals, backgroundColor:colors, borderRadius:6}]},
    options:{plugins:{legend:{display:false}}, scales:{y:{min:0,max:1}}}
  });
}
modelChart('ch-models-syn-eff', DATA.models.synthetic_eff);
modelChart('ch-models-real-eff', DATA.models.real_eff);
modelChart('ch-models-syn-gas', DATA.models.synthetic_gas);

// 8) جدول توالی بهینه
const seq = DATA.optimal_seq_top30;
const tbody = document.getElementById('seq-body');
seq.order_ids.forEach((oid,i)=>{
  const tr = document.createElement('tr');
  const cls = 'p-'+seq.flute[i];
  const prioCls = 'prio-'+seq.priority[i];
  tr.innerHTML = '<td>'+faNum(i+1)+'</td><td>'+oid+'</td>'+
    '<td><span class="pill '+cls+'">'+seq.flute[i]+'</span></td>'+
    '<td>'+seq.temps[i]+'</td><td>'+seq.weight[i]+'</td>'+
    '<td class="'+prioCls+'">'+faNum(seq.priority[i])+'</td>';
  tbody.appendChild(tr);
});
</script>
</body>
</html>
"""

html = (HTML
  .replace("__DATA_JSON__", json.dumps(data, ensure_ascii=False))
)
out = ROOT / "ai_dashboard.html"
out.write_text(html, encoding="utf-8")
print(f"ai_dashboard.html written, {out.stat().st_size} bytes")
