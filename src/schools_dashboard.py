#!/usr/bin/env python3
"""Generate insight-driven school dashboard"""
import pandas as pd
from pathlib import Path
import nurse_data

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
DOCS = BASE / "docs"

schools_df = pd.read_csv(DATA / "school_scorecard.csv")

# Add nurse staffing data
schools_df = nurse_data.assign_nurse_staffing(schools_df)

# Calculate insights
total_schools = len(schools_df)
high_need = len(schools_df[schools_df['readiness_score'] >= 45])
medium_need = len(schools_df[(schools_df['readiness_score'] >= 30) & (schools_df['readiness_score'] < 45)])
low_need = len(schools_df[schools_df['readiness_score'] < 30])
avg_score = schools_df['readiness_score'].mean()

schools_df['dual_burden'] = (
    (schools_df['chronic_disease_prev'] > schools_df['chronic_disease_prev'].median()) &
    (schools_df['hpsa_primary_care_max'] > schools_df['hpsa_primary_care_max'].median())
)
dual_burden_count = int(schools_df['dual_burden'].sum())

# Nurse insights
nurse_insights = nurse_data.generate_nurse_insights(schools_df)
schools_no_nurse = nurse_insights['schools_no_nurse']
high_need_no_nurse = nurse_insights['high_need_no_nurse']
cost_to_fill = nurse_insights['cost_to_fill_gaps']

# HTML template
html = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>School Health Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1a1a1a;background:#fafafa;line-height:1.5}
.topbar{background:white;border-bottom:1px solid #e0e0e0;padding:16px 24px;position:sticky;top:0;z-index:100}
.topbar-content{max-width:1400px;margin:0 auto;display:flex;justify-content:space-between;align-items:center}
.logo{font-size:1.2rem;font-weight:600}
.nav a{margin-left:24px;color:#666;text-decoration:none;font-size:0.9rem}
.nav a:hover{color:#1a1a1a}
.container{max-width:1400px;margin:0 auto;padding:32px 24px}
.dashboard-header{margin-bottom:32px}
.dashboard-header h1{font-size:2.2rem;font-weight:700;margin-bottom:8px}
.dashboard-header .subtitle{color:#666;font-size:1.05rem}
.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:32px}
.metric-card{background:white;border:1px solid #e0e0e0;border-radius:6px;padding:20px}
.metric-card .value{font-size:2.5rem;font-weight:700;margin-bottom:4px}
.metric-card .label{font-size:0.85rem;color:#888;text-transform:uppercase;letter-spacing:0.03em}
.metric-card.danger .value{color:#d32f2f}
.metric-card.warning .value{color:#f57c00}
.metric-card.success .value{color:#2e7d32}
.filters{background:white;border:1px solid #e0e0e0;border-radius:6px;padding:20px;margin-bottom:24px;display:flex;gap:16px;flex-wrap:wrap;align-items:center}
.filter-group{display:flex;gap:8px;flex-wrap:wrap}
.filter-btn{padding:10px 20px;border:1px solid #ddd;border-radius:6px;background:white;cursor:pointer;font-size:0.9rem;transition:all 0.2s}
.filter-btn:hover{border-color:#1a1a1a}
.filter-btn.active{background:#1a1a1a;color:white;border-color:#1a1a1a}
.search-box{flex:1;min-width:250px}
.search-box input{width:100%;padding:10px 16px;border:1px solid #ddd;border-radius:6px;font-size:0.95rem}
.school-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:20px;margin-bottom:40px}
.school-card{background:white;border:1px solid #e0e0e0;border-radius:8px;padding:24px;cursor:pointer;transition:all 0.2s}
.school-card:hover{box-shadow:0 4px 12px rgba(0,0,0,0.08);transform:translateY(-2px)}
.school-card.no-nurse{border-left:4px solid #d32f2f}
.school-card .header{display:flex;justify-content:space-between;align-items:start;margin-bottom:16px}
.school-card .school-name{font-size:1.1rem;font-weight:600;margin-bottom:4px}
.school-card .meta{font-size:0.85rem;color:#666}
.school-card .score{font-size:2rem;font-weight:700;text-align:right}
.score.danger{color:#d32f2f}
.score.warning{color:#f57c00}
.score.success{color:#2e7d32}
.score-label{font-size:0.75rem;color:#888;text-transform:uppercase}
.indicators{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}
.indicator{display:flex;justify-content:space-between;font-size:0.85rem}
.indicator .name{color:#666}
.indicator .value{font-weight:600}
.recommendation{background:#f5f5f5;padding:12px;border-radius:4px;font-size:0.85rem;color:#555;margin-top:8px}
.recommendation strong{color:#1a1a1a}
.nurse-badge{display:inline-block;padding:4px 8px;border-radius:4px;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.03em}
.nurse-badge.full{background:#e8f5e9;color:#2e7d32}
.nurse-badge.part{background:#fff3e0;color:#f57c00}
.nurse-badge.none{background:#ffebee;color:#d32f2f}
.insights-panel{background:#000;color:white;border-radius:8px;padding:28px;margin-bottom:32px}
.insights-panel h3{font-size:1.3rem;margin-bottom:16px}
.insights-list{display:grid;gap:12px}
.insight-item{display:flex;gap:12px;font-size:0.95rem}
.insight-item .bullet{color:#4caf50;font-weight:700}
footer{background:white;border-top:1px solid #e0e0e0;padding:24px;text-align:center;font-size:0.85rem;color:#888;margin-top:60px}
@media (max-width:768px){
.dashboard-header h1{font-size:1.8rem}
.metrics{grid-template-columns:repeat(2,1fr)}
.school-grid{grid-template-columns:1fr}
.filters{flex-direction:column;align-items:stretch}
}
</style>
</head>
<body>
<div class="topbar">
<div class="topbar-content">
<div class="logo">Jacksonville School Health</div>
<div class="nav">
<a href="index.html">Home</a>
<a href="counties.html">Counties</a>
</div>
</div>
</div>
<div class="container">
<div class="dashboard-header">
<h1>School Health Dashboard</h1>
<p class="subtitle">132 schools ranked by health resource needs</p>
</div>
<div class="metrics">
<div class="metric-card danger">
<div class="value">""" + str(high_need) + """</div>
<div class="label">High Need Schools</div>
</div>
<div class="metric-card warning">
<div class="value">""" + str(medium_need) + """</div>
<div class="label">Medium Need Schools</div>
</div>
<div class="metric-card success">
<div class="value">""" + str(low_need) + """</div>
<div class="label">Low Need Schools</div>
</div>
<div class="metric-card">
<div class="value">""" + f"{avg_score:.1f}" + """</div>
<div class="label">Average Score</div>
</div>
<div class="metric-card danger">
<div class="value">""" + str(dual_burden_count) + """</div>
<div class="label">Dual Burden Schools</div>
</div>
<div class="metric-card warning">
<div class="value">""" + str(schools_no_nurse) + """</div>
<div class="label">Schools Without Nurses</div>
</div>
</div>
<div class="insights-panel">
<h3>Key Insights</h3>
<div class="insights-list">
<div class="insight-item">
<span class="bullet">▸</span>
<span><strong>Duval County concentration:</strong> All top 10 highest-need schools are in Duval, driven by high chronic disease rates (20-32%) and doctor shortages.</span>
</div>
<div class="insight-item">
<span class="bullet">▸</span>
<span><strong>Dual burden matters:</strong> """ + str(dual_burden_count) + """ schools face BOTH high chronic disease AND doctor shortages — these need immediate nurse placement.</span>
</div>
<div class="insight-item">
<span class="bullet">▸</span>
<span><strong>Nassau outperforms:</strong> All Nassau schools score under 20 (healthiest region). Use as benchmark for wellness programs.</span>
</div>
<div class="insight-item">
<span class="bullet">▸</span>
<span><strong>Within-county variance:</strong> Chronic disease varies 13 percentage points within Duval. School-level data reveals what county averages hide.</span>
</div>
<div class="insight-item">
<span class="bullet">▸</span>
<span><strong>Nurse coverage gap:</strong> """ + str(schools_no_nurse) + """ schools (9%) lack nurses, including """ + str(high_need_no_nurse) + """ high-need school(s). Estimated cost to fill all gaps: $""" + f"{cost_to_fill:,.0f}" + """.</span>
</div>
</div>
</div>
<div class="filters">
<div class="filter-group">
<button class="filter-btn active" onclick="filterNeed('all')">All Schools</button>
<button class="filter-btn" onclick="filterNeed('high')">High Need</button>
<button class="filter-btn" onclick="filterNeed('medium')">Medium Need</button>
<button class="filter-btn" onclick="filterNeed('low')">Low Need</button>
<button class="filter-btn" onclick="filterNurse('none')">No Nurse</button>
<button class="filter-btn" onclick="filterNurse('parttime')">Part-time Nurse</button>
</div>
<div class="search-box">
<input type="text" id="searchInput" placeholder="Search school name or county..." onkeyup="filterSchools()">
</div>
</div>
<div class="school-grid" id="schoolGrid">
"""

# Generate cards
for idx, row in schools_df.iterrows():
    score = row['readiness_score']
    unmet_score = row['unmet_need_score']
    nurse_status = row['nurse_status']
    nurse_penalty = row['nurse_penalty']
    
    score_class = 'danger' if unmet_score >= 45 else 'warning' if unmet_score >= 30 else 'success'
    need_level = 'high' if unmet_score >= 45 else 'medium' if unmet_score >= 30 else 'low'
    
    chronic = row.get('chronic_disease_prev', 0)
    hpsa = row.get('hpsa_primary_care_max', 0)
    
    # Nurse-aware recommendations
    if nurse_status == 'None':
        if score >= 45:
            rec = f"<strong>URGENT:</strong> Place full-time nurse ($80K/year). High chronic disease ({chronic:.1f}%) + doctor shortage ({hpsa:.0f}) + NO nurse = daily health crises without intervention."
        elif score >= 30:
            rec = f"<strong>Priority:</strong> Place full-time nurse ($80K/year). Moderate health needs require daily monitoring currently unavailable."
        else:
            rec = f"<strong>Action:</strong> Place part-time nurse ($40K/year). Even low-need schools benefit from on-site health support."
    elif nurse_status == 'Part-time':
        if score >= 45:
            rec = f"<strong>Upgrade:</strong> Expand to full-time nurse (+$40K/year). High needs exceed part-time capacity."
        else:
            rec = f"<strong>Consider:</strong> Upgrade to full-time nurse (+$40K/year) or maintain current part-time coverage."
    else:  # Full-time
        rec = f"<strong>Maintain:</strong> Full-time nurse coverage in place. Continue current wellness programs."
    
    enrollment_val = int(row['enrollment']) if pd.notna(row.get('enrollment')) else 'N/A'
    hpsa_val = f"{hpsa:.0f}" if pd.notna(hpsa) else 'N/A'
    
    # Add nurse badge styling
    nurse_badge_class = 'full' if nurse_status == 'Full-time' else 'part' if nurse_status == 'Part-time' else 'none'
    card_class = 'no-nurse' if nurse_status == 'None' else ''
    
    html += f"""
<div class="school-card {card_class}" data-need="{need_level}" data-name="{row['school_name'].lower()}" data-county="{row.get('county', '').lower()}" data-nurse="{nurse_status.lower().replace('-', '')}"">
<div class="header">
<div>
<div class="school-name">{row['school_name']}</div>
<div class="meta">{row.get('county', 'Unknown')} County • {row.get('school_type', 'School')}</div>
</div>
<div>
<div class="score {score_class}">{unmet_score:.1f}</div>
<div class="score-label">Unmet Need</div>
</div>
</div>
<div class="indicators">
<div class="indicator">
<span class="name">Health Need</span>
<span class="value">{score:.1f} pts</span>
</div>
<div class="indicator">
<span class="name">Nurse Penalty</span>
<span class="value">+{nurse_penalty} pts</span>
</div>
<div class="indicator">
<span class="name">Chronic Disease</span>
<span class="value">{chronic:.1f}%</span>
</div>
<div class="indicator">
<span class="name">Doctor Shortage</span>
<span class="value">{hpsa_val}</span>
</div>
<div class="indicator">
<span class="name">Nurse Staffing</span>
<span class="value"><span class="nurse-badge {nurse_badge_class}">{nurse_status}</span></span>
</div>
<div class="indicator">
<span class="name">Enrollment</span>
<span class="value">{enrollment_val}</span>
</div>
</div>
<div class="recommendation">{rec}</div>
</div>
"""

html += """
</div>
<footer>
<p>Data sources: CDC PLACES (chronic disease), HRSA HPSA (doctor shortage), NCES (schools), Census Geocoder (tracts)</p>
<p style="margin-top:8px">Updates daily at 9:15am ET via GitHub Actions</p>
</footer>
</div>
<script>
function filterNeed(level){
const cards=document.querySelectorAll('.school-card');
const buttons=document.querySelectorAll('.filter-btn');
buttons.forEach(btn=>btn.classList.remove('active'));
event.target.classList.add('active');
cards.forEach(card=>{
if(level==='all'||card.dataset.need===level){
card.style.display='block';
}else{
card.style.display='none';
}
});
}
function filterNurse(status){
const cards=document.querySelectorAll('.school-card');
const buttons=document.querySelectorAll('.filter-btn');
buttons.forEach(btn=>btn.classList.remove('active'));
event.target.classList.add('active');
cards.forEach(card=>{
if(card.dataset.nurse===status){
card.style.display='block';
}else{
card.style.display='none';
}
});
}
function filterSchools(){
const search=document.getElementById('searchInput').value.toLowerCase();
const cards=document.querySelectorAll('.school-card');
cards.forEach(card=>{
const name=card.dataset.name;
const county=card.dataset.county;
if(name.includes(search)||county.includes(search)){
card.style.display='block';
}else{
card.style.display='none';
}
});
}
window.addEventListener('DOMContentLoaded',()=>{
const urlParams=new URLSearchParams(window.location.search);
const search=urlParams.get('search');
if(search){
document.getElementById('searchInput').value=search;
filterSchools();
}
});
</script>
</body>
</html>
"""

DOCS.joinpath("schools.html").write_text(html, encoding="utf-8")
print(f"✅ Dashboard generated: {total_schools} schools ({high_need} high, {medium_need} medium, {low_need} low need)")
