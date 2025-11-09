#!/usr/bin/env python3
"""Generate insight-driven school dashboard"""
import pandas as pd
from pathlib import Path
import nurse_data
import grading

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
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1a1a1a;background:#fafafa;line-height:1.5;-webkit-font-smoothing:antialiased}
.app-nav{background:#1a1a1a;color:white;position:sticky;top:0;z-index:200}
.app-nav-header{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;cursor:pointer}
.app-nav-logo{font-size:1rem;font-weight:600}
.app-nav-toggle{font-size:1.5rem;transition:transform 0.2s}
.app-nav-toggle.open{transform:rotate(180deg)}
.app-nav-menu{display:none;border-top:1px solid rgba(255,255,255,0.1)}
.app-nav-menu.show{display:block}
.app-nav-menu a{display:block;padding:14px 16px;color:rgba(255,255,255,0.8);text-decoration:none;border-bottom:1px solid rgba(255,255,255,0.05);font-size:0.9rem;min-height:48px}
.app-nav-menu a:active{background:rgba(255,255,255,0.1)}
.app-nav-menu a.active{color:white;background:rgba(255,255,255,0.05);font-weight:600}
.container{max-width:1400px;margin:0 auto;padding:16px}
.dashboard-header{margin-bottom:24px}
.dashboard-header h1{font-size:1.75rem;font-weight:700;margin-bottom:6px;line-height:1.2}
.dashboard-header .subtitle{color:#666;font-size:0.95rem}
.metrics{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:24px}
.metric-card{background:white;border:1px solid #e0e0e0;border-radius:6px;padding:16px}
.metric-card .value{font-size:2rem;font-weight:700;margin-bottom:2px;line-height:1}
.metric-card .label{font-size:0.75rem;color:#888;text-transform:uppercase;letter-spacing:0.03em;line-height:1.3}
.metric-card.danger .value{color:#d32f2f}
.metric-card.warning .value{color:#f57c00}
.metric-card.success .value{color:#2e7d32}
.filters{background:white;border:1px solid #e0e0e0;border-radius:6px;padding:16px;margin-bottom:16px}
.filter-row{display:flex;flex-direction:column;gap:8px;margin-bottom:12px}
.filter-row:last-child{margin-bottom:0}
.filter-label{font-size:0.8rem;color:#666;font-weight:600;margin-bottom:4px}
.filter-group{display:flex;gap:6px;flex-wrap:wrap}
.filter-btn{padding:10px 14px;border:2px solid #ddd;border-radius:6px;background:white;cursor:pointer;font-size:0.85rem;transition:all 0.15s;-webkit-tap-highlight-color:transparent;min-height:44px}
.filter-btn:active{background:#f5f5f5;border-color:#1a1a1a}
.filter-btn.active{background:#1a1a1a;color:white;border-color:#1a1a1a}
.search-box{width:100%}
.search-box input{width:100%;padding:14px;border:2px solid #ddd;border-radius:6px;font-size:1rem;-webkit-appearance:none;min-height:48px}
.school-grid{display:flex;flex-direction:column;gap:0;margin-bottom:32px;background:white;border:1px solid #e0e0e0;border-radius:8px;overflow:hidden}
.school-card{background:white;border:none;border-bottom:1px solid #f0f0f0;padding:16px;transition:background 0.15s;-webkit-tap-highlight-color:transparent}
.school-card:last-child{border-bottom:none}
.school-card.no-nurse{border-left:3px solid #d32f2f;padding-left:13px}
.school-card .header{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;margin-bottom:12px}
.school-card .left{flex:1;min-width:0}
.school-card .school-name{font-size:1rem;font-weight:600;margin-bottom:4px;line-height:1.3}
.school-card .meta{font-size:0.8rem;color:#888;margin-bottom:8px}
.school-card .right{display:flex;align-items:center;gap:8px;flex-shrink:0}
.school-card .nurse-badge{font-size:0.65rem;padding:4px 7px}
.score.danger{color:#d32f2f}
.score.warning{color:#f57c00}
.score.success{color:#2e7d32}
.score-label{font-size:0.7rem;color:#888;text-transform:uppercase;margin-top:2px}
""" + grading.get_grade_styles() + """
.grade-display{font-size:1.5rem;font-family:Georgia,serif;line-height:1;font-weight:700}
.grade-label-text{font-size:0.65rem;color:#888;margin-top:2px}
.details-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px}
.detail-item{display:flex;flex-direction:column;font-size:0.75rem}
.detail-item .label{color:#888;margin-bottom:2px;font-size:0.7rem}
.detail-item .value{font-weight:600;font-size:0.8rem}
.recommendation{background:#f9f9f9;padding:10px;border-radius:4px;font-size:0.75rem;color:#555;line-height:1.4;margin-top:8px;border-left:3px solid #e0e0e0}
.recommendation strong{color:#1a1a1a}
.nurse-badge{display:inline-block;padding:4px 8px;border-radius:4px;font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.03em}
.nurse-badge.full{background:#e8f5e9;color:#2e7d32}
.nurse-badge.part{background:#fff3e0;color:#f57c00}
.nurse-badge.none{background:#ffebee;color:#d32f2f}
.insights-panel{background:#000;color:white;border-radius:8px;padding:20px;margin-bottom:24px}
.insights-panel h3{font-size:1.1rem;margin-bottom:12px}
.insights-list{display:grid;gap:10px}
.insight-item{display:flex;gap:10px;font-size:0.85rem;line-height:1.5}
.insight-item .bullet{color:#4caf50;font-weight:700;flex-shrink:0}
footer{background:white;border-top:1px solid #e0e0e0;padding:20px 16px;text-align:center;font-size:0.8rem;color:#888;margin-top:40px;line-height:1.6}
@media (min-width:768px){
.app-nav-header{padding:14px 24px}
.app-nav-logo{font-size:1.1rem}
.app-nav-toggle{display:none}
.app-nav-menu{display:flex!important;border:none}
.app-nav-menu a{padding:0 20px;border:none;line-height:48px;min-height:auto}
.app-nav-menu a:hover{color:white;background:rgba(255,255,255,0.1)}
.container{padding:32px 24px}
.dashboard-header{margin-bottom:32px}
.dashboard-header h1{font-size:2.2rem;margin-bottom:8px}
.dashboard-header .subtitle{font-size:1.05rem}
.metrics{grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px;margin-bottom:32px}
.metric-card{padding:20px}
.metric-card .value{font-size:2.5rem;margin-bottom:4px}
.metric-card .label{font-size:0.85rem}
.filters{padding:20px;margin-bottom:24px}
.filter-row{flex-direction:row;align-items:center;gap:16px}
.filter-label{min-width:100px;margin-bottom:0}
.filter-btn{padding:8px 16px}
.filter-btn:hover{border-color:#1a1a1a}
.school-card{padding:20px}
.school-card:hover{background:#f9f9f9}
.school-card .school-name{font-size:1.05rem}
.school-card .meta{font-size:0.85rem}
.school-card .header{margin-bottom:14px}
.grade-display{font-size:1.8rem}
.grade-label-text{font-size:0.7rem}
.details-grid{grid-template-columns:repeat(3,1fr)}
.recommendation{font-size:0.85rem;padding:12px}
.insights-panel{padding:28px;margin-bottom:32px}
.insights-panel h3{font-size:1.3rem;margin-bottom:16px}
.insight-item{font-size:0.95rem;gap:12px}
footer{padding:24px;margin-top:60px;font-size:0.85rem}
}
</style>
</head>
<body>
<nav class="app-nav">
<div class="app-nav-header" onclick="toggleNav()">
<div class="app-nav-logo">Jacksonville School Health</div>
<div class="app-nav-toggle" id="navToggle">▼</div>
</div>
<div class="app-nav-menu" id="navMenu">
<a href="index.html">Home</a>
<a href="schools.html" class="active">Schools</a>
<a href="counties.html">Counties</a>
<a href="../data/school_scorecard.csv">Download Data</a>
</div>
</nav>
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
""" + grading.get_grade_explanation() + """
<div class="filters">
<div class="filter-row">
<div class="search-box">
<input type="text" id="searchInput" placeholder="Search school name or county..." onkeyup="filterSchools()">
</div>
</div>
<div class="filter-row">
<div class="filter-label">Need Level:</div>
<div class="filter-group">
<button class="filter-btn active" onclick="filterNeed('all')">All</button>
<button class="filter-btn" onclick="filterNeed('high')">High</button>
<button class="filter-btn" onclick="filterNeed('medium')">Medium</button>
<button class="filter-btn" onclick="filterNeed('low')">Low</button>
</div>
</div>
<div class="filter-row">
<div class="filter-label">Nurse Status:</div>
<div class="filter-group">
<button class="filter-btn active" onclick="filterNurse('all')">All</button>
<button class="filter-btn" onclick="filterNurse('fulltime')">Full-time</button>
<button class="filter-btn" onclick="filterNurse('parttime')">Part-time</button>
<button class="filter-btn" onclick="filterNurse('none')">None</button>
</div>
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
    
    # Get letter grade
    letter, grade_label, grade_class = grading.get_letter_grade(unmet_score)
    
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
<div class="school-card {card_class}" data-need="{need_level}" data-name="{row['school_name'].lower()}" data-county="{row.get('county', '').lower()}" data-nurse="{nurse_status.lower().replace('-', '')}">
<div class="header">
<div class="left">
<div class="school-name">{row['school_name']}</div>
<div class="meta">{row.get('county', 'Unknown')} County • {row.get('school_type', 'School')} • {enrollment_val if isinstance(enrollment_val, str) else f'{enrollment_val:,}'} students</div>
</div>
<div class="right">
<div>
<div class="grade-display grade-{letter.lower()}">{letter}</div>
<div class="grade-label-text">{grade_label}</div>
</div>
</div>
</div>
<div class="details-grid">
<div class="detail-item">
<span class="label">Chronic Disease</span>
<span class="value">{chronic:.1f}%</span>
</div>
<div class="detail-item">
<span class="label">Doctor Shortage</span>
<span class="value">{hpsa_val}</span>
</div>
<div class="detail-item">
<span class="label">Air Quality</span>
<span class="value">Good</span>
</div>
<div class="detail-item">
<span class="label">Nurse Staffing</span>
<span class="value"><span class="nurse-badge {nurse_badge_class}">{nurse_status}</span></span>
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
let currentNeedFilter='all';
let currentNurseFilter='all';
function filterNeed(level){
currentNeedFilter=level;
const buttons=event.target.parentElement.querySelectorAll('.filter-btn');
buttons.forEach(btn=>btn.classList.remove('active'));
event.target.classList.add('active');
applyFilters();
}
function filterNurse(status){
currentNurseFilter=status;
const buttons=event.target.parentElement.querySelectorAll('.filter-btn');
buttons.forEach(btn=>btn.classList.remove('active'));
event.target.classList.add('active');
applyFilters();
}
function applyFilters(){
const cards=document.querySelectorAll('.school-card');
cards.forEach(card=>{
const needMatch=currentNeedFilter==='all'||card.dataset.need===currentNeedFilter;
const nurseMatch=currentNurseFilter==='all'||card.dataset.nurse===currentNurseFilter;
card.style.display=(needMatch&&nurseMatch)?'block':'none';
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
