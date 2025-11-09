#!/usr/bin/env python3
"""
Phase 4: School-Level HTML Visualization Generator
Creates interactive, searchable school health readiness table.
"""
import pandas as pd
import pathlib
import json
from datetime import datetime

BASE = pathlib.Path(__file__).resolve().parents[1]
OUT = BASE / "data"
DOCS = BASE / "docs"


def generate_school_html(schools_df: pd.DataFrame) -> str:
    """
    Generate comprehensive HTML page for school-level scorecard.
    Features: Search, filter by county, sortable columns.
    """
    
    # Statistics
    total_schools = len(schools_df)
    schools_with_tracts = schools_df["tract"].notna().sum()
    avg_score = schools_df["readiness_score"].mean()
    
    # County breakdown
    county_counts = schools_df["county"].value_counts().to_dict()
    
    title = "School Rankings - Jacksonville School Health"
    
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Interactive rankings for {total_schools} Jacksonville-area K-12 schools based on health indicators">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* {{box-sizing: border-box}}
body {{
    font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
    margin: 0;
    padding: 0;
    background: #f5f5f5;
}}
nav {{background: #1976d2; color: white; padding: 16px 24px; margin-bottom: 0}}
nav .nav-content {{max-width: 1400px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap}}
nav .logo {{font-size: 1.3rem; font-weight: 600; color: white; text-decoration: none}}
nav .links {{display: flex; gap: 24px}}
nav a {{color: white; text-decoration: none; font-size: 0.95rem; transition: opacity 0.2s}}
nav a:hover {{opacity: 0.8}}
nav .active {{font-weight: 600; border-bottom: 2px solid white; padding-bottom: 2px}}

.container {{max-width: 1400px; margin: 0 auto; background: white; padding: 32px; border-radius: 0}}
h1 {{margin: 0; font-size: 2.2rem; color: #1a1a1a; font-weight: 700}}
h2 {{margin: 12px 0 24px; color: #666; font-weight: 400; font-size: 1.15rem}}

.stats-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin: 24px 0;
}}
.stat-card {{
    background: #f9f9f9;
    padding: 16px;
    border-radius: 6px;
    border-left: 4px solid #4CAF50;
}}
.stat-card h3 {{margin: 0 0 8px 0; font-size: 0.85rem; text-transform: uppercase; color: #666; font-weight: 600}}
.stat-card .value {{font-size: 2rem; font-weight: bold; color: #1a1a1a}}
.stat-card .label {{font-size: 0.85rem; color: #888; margin-top: 4px}}

.controls {{
    display: flex;
    gap: 16px;
    margin: 24px 0;
    flex-wrap: wrap;
    align-items: center;
}}
.search-box {{
    flex: 1;
    min-width: 250px;
}}
.search-box input {{
    width: 100%;
    padding: 10px 14px;
    border: 2px solid #ddd;
    border-radius: 6px;
    font-size: 1rem;
}}
.search-box input:focus {{
    outline: none;
    border-color: #4CAF50;
}}
.filter-group {{display: flex; gap: 8px; align-items: center}}
.filter-group label {{font-weight: 600; color: #666; font-size: 0.9rem}}
.filter-group select {{
    padding: 8px 12px;
    border: 2px solid #ddd;
    border-radius: 6px;
    font-size: 0.95rem;
}}

.legend {{
    background: #e8f5e9;
    border-left: 4px solid #4CAF50;
    padding: 16px;
    margin: 20px 0;
    border-radius: 4px;
}}
.legend h3 {{margin: 0 0 12px 0; font-size: 0.95rem; text-transform: uppercase; color: #2e7d32}}
.legend ul {{margin: 0; padding-left: 20px}}
.legend li {{font-size: 0.9rem; color: #555; margin: 6px 0}}

.charts-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 24px;
    margin: 24px 0;
}}
.chart-card {{
    background: white;
    padding: 20px;
    border-radius: 8px;
    border: 1px solid #ddd;
}}
.chart-card h3 {{margin: 0 0 16px 0; font-size: 1rem; color: #333}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 16px;
    font-size: 0.9rem;
}}
thead {{position: sticky; top: 0; background: #f7f7f7; z-index: 10}}
th, td {{
    border: 1px solid #ddd;
    padding: 12px 10px;
    text-align: left;
}}
th {{
    background: #f7f7f7;
    font-weight: 600;
    font-size: 0.85rem;
    cursor: pointer;
    user-select: none;
}}
th:hover {{background: #eee}}
td {{vertical-align: middle}}

.rank {{font-weight: bold; color: #666}}
.school-name {{font-weight: 600; color: #1a1a1a}}
.score {{font-weight: bold; font-size: 1.1rem}}
.score-high {{color: #d32f2f}}
.score-medium {{color: #f57c00}}
.score-low {{color: #4CAF50}}

.county-badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 3px;
    font-size: 0.75rem;
    font-weight: 600;
    background: #e3f2fd;
    color: #1976d2;
}}

.enrollment {{color: #666; font-size: 0.85rem}}
.no-data {{color: #999; font-style: italic}}

footer {{
    margin-top: 32px;
    padding-top: 16px;
    border-top: 2px solid #eee;
    color: #666;
    font-size: 0.85rem;
}}
footer a {{color: #1976d2; text-decoration: none}}
footer a:hover {{text-decoration: underline}}

.hidden {{display: none}}
</style>
</head>
<body>
<div class="container">

<div class="stats-grid">
    <div class="stat-card">
        <h3>Total Schools</h3>
        <div class="value">{total_schools}</div>
        <div class="label">Across 5 counties</div>
    </div>
    <div class="stat-card">
        <h3>Geocoded</h3>
        <div class="value">{schools_with_tracts}</div>
        <div class="label">With tract-level data ({schools_with_tracts/total_schools*100:.1f}%)</div>
    </div>
    <div class="stat-card">
        <h3>Average Score</h3>
        <div class="value">{avg_score:.1f}</div>
        <div class="label">Out of 100 points</div>
    </div>
    <div class="stat-card">
        <h3>Highest Need</h3>
        <div class="value">{schools_df.iloc[0]['readiness_score']:.1f}</div>
        <div class="label">{schools_df.iloc[0]['school_name'][:30]}</div>
    </div>
</div>

<div class="legend">
<h3>📊 How We Calculate Health Scores (100 Points Total)</h3>
<ul>
<li><strong>Doctor Availability (30 pts):</strong> How easy is it to find a doctor in your county</li>
<li><strong>Neighborhood Health (30 pts):</strong> % of people nearby with diabetes, obesity, or asthma</li>
<li><strong>Air Quality (15 pts):</strong> Days with unhealthy air in your county</li>
<li><strong>Natural Disaster Risk (15 pts):</strong> Risk of hurricanes, flooding, etc.</li>
<li><strong>Respiratory Illness (10 pts):</strong> Current flu/COVID/RSV activity in Florida</li>
</ul>
<p style="margin: 12px 0 0 0; color: #666; font-size: 0.9rem;">
<strong>Higher score = school area has more health challenges.</strong> Most schools use neighborhood-specific data.
</p>
</div>

"""
    
    # Add county filter options
    for county in sorted(schools_df["county"].unique()):
        count = county_counts.get(county, 0)
        html += f'            <option value="{county}">{county} ({count})</option>\n'
    
    html += """        </select>
    </div>
    <div class="filter-group">
        <label for="scoreFilter">Score:</label>
        <select id="scoreFilter" onchange="filterTable()">
            <option value="">All Scores</option>
            <option value="high">High Need (45+)</option>
            <option value="medium">Medium Need (30-45)</option>
            <option value="low">Low Need (<30)</option>
        </select>
    </div>
</div>

<div class="info-box" style="background:#e3f2fd;border-left:4px solid #1976d2;padding:24px;margin:32px 0;border-radius:8px">
<h3 style="margin:0 0 16px 0;color:#1976d2;font-size:1.3rem">📖 Understanding School Health Scores</h3>

<div style="background:white;padding:20px;border-radius:6px;margin-bottom:20px">
<p style="margin-bottom:16px;font-size:1.05rem;color:#333">
Each school receives a <strong>Health Need Score (0-100)</strong> based on 5 factors in its area. 
<strong>Higher score = more health challenges</strong> that may affect students.
</p>

<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px;margin-top:16px">
  <div style="padding:16px;background:#ffebee;border-radius:6px;border-left:3px solid #d32f2f">
    <strong style="color:#d32f2f">40-50: High Need</strong>
    <p style="margin:8px 0 0;font-size:0.95rem;color:#555">Area has significant health challenges. May need additional nurses, wellness programs, or health screenings.</p>
  </div>
  <div style="padding:16px;background:#fff3e0;border-radius:6px;border-left:3px solid #f57c00">
    <strong style="color:#f57c00">30-40: Medium Need</strong>
    <p style="margin:8px 0 0;font-size:0.95rem;color:#555">Moderate health factors present. Standard health programs recommended.</p>
  </div>
  <div style="padding:16px;background:#e8f5e9;border-radius:6px;border-left:3px solid #2e7d32">
    <strong style="color:#2e7d32">15-30: Low Need</strong>
    <p style="margin:8px 0 0;font-size:0.95rem;color:#555">Relatively healthy area. Maintain existing health support programs.</p>
  </div>
</div>
</div>

<details style="margin-top:20px">
<summary style="font-size:1.05rem">🔍 What Do The Individual Indicators Mean? (Click to expand)</summary>
<div style="padding:16px 0">

<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px">

<div>
<h4 style="color:#1976d2;margin-bottom:8px">🏥 Neighborhood Health (30 pts)</h4>
<p style="font-size:0.95rem;color:#555;line-height:1.6">
<strong>What it is:</strong> % of people in the school's neighborhood with diabetes, obesity, or asthma.<br>
<strong>Why it matters:</strong> Higher rates = students more likely to have health needs.<br>
<strong>US Average:</strong> ~20%<br>
<strong>Range here:</strong> 10-32%
</p>
</div>

<div>
<h4 style="color:#1976d2;margin-bottom:8px">👨‍⚕️ Doctor Availability (30 pts)</h4>
<p style="font-size:0.95rem;color:#555;line-height:1.6">
<strong>What it is:</strong> Healthcare shortage score for the county (0-25 scale).<br>
<strong>Why it matters:</strong> Harder to find doctors = families struggle to get care.<br>
<strong>25 = severe shortage</strong> (Duval)<br>
<strong>11 = less shortage</strong> (Nassau)
</p>
</div>

<div>
<h4 style="color:#1976d2;margin-bottom:8px">💨 Air Quality (15 pts)</h4>
<p style="font-size:0.95rem;color:#555;line-height:1.6">
<strong>What it is:</strong> Days per year with unhealthy air in the county.<br>
<strong>Why it matters:</strong> Poor air quality worsens asthma, affects outdoor activities.<br>
<strong>Most counties:</strong> 0 unhealthy days (good!)
</p>
</div>

<div>
<h4 style="color:#1976d2;margin-bottom:8px">🌪️ Natural Disaster Risk (15 pts)</h4>
<p style="font-size:0.95rem;color:#555;line-height:1.6">
<strong>What it is:</strong> County's risk from hurricanes, flooding, storms.<br>
<strong>Why it matters:</strong> Emergency preparedness, evacuation planning, resilience.<br>
<strong>Current:</strong> Low risk across region
</p>
</div>

<div>
<h4 style="color:#1976d2;margin-bottom:8px">🦠 Respiratory Illness (10 pts)</h4>
<p style="font-size:0.95rem;color:#555;line-height:1.6">
<strong>What it is:</strong> Current flu/COVID/RSV activity level in Florida.<br>
<strong>Why it matters:</strong> High activity = more student absences, spread prevention needed.<br>
<strong>Current:</strong> Minimal activity (2 pts)
</p>
</div>

</div>

</div>
</details>

<details>
<summary style="font-size:1.05rem">💡 What Can Be Done to Improve a School's Score? (Click to expand)</summary>
<div style="padding:16px 0;line-height:1.7">

<strong>For Parents:</strong>
<ul style="margin:12px 0">
<li>✓ Ask: "Do we have a full-time school nurse?"</li>
<li>✓ Request: Wellness programs and health screenings</li>
<li>✓ Support: PTA health committees</li>
<li>✓ At home: Healthy eating, daily physical activity, regular checkups</li>
</ul>

<strong>For Schools & Administrators:</strong>
<ul style="margin:12px 0">
<li>✓ Apply for federal wellness grants (use this data to justify need)</li>
<li>✓ Hire or expand school nurse coverage</li>
<li>✓ Partner with local clinics for free student health screenings</li>
<li>✓ Improve lunch nutrition and increase PE time</li>
<li>✓ Install air quality monitors and HEPA filters</li>
<li>✓ Launch chronic disease prevention programs</li>
</ul>

<strong>For District Leadership:</strong>
<ul style="margin:12px 0">
<li>✓ Compare schools to identify which need resources most</li>
<li>✓ Use tract-level data for targeted interventions (not county-wide)</li>
<li>✓ Track improvements over time (data updates daily)</li>
<li>✓ Justify budget requests with objective federal data</li>
</ul>

</div>
</details>

<details>
<summary style="font-size:1.05rem">📈 Example: What Does a Score of 35 Mean? (Click to expand)</summary>
<div style="padding:16px 0">

<div style="background:white;padding:20px;border-radius:6px;border:1px solid #e0e0e0">
<h4 style="color:#f57c00;margin-bottom:12px">Example School: Score 35 (Medium Need)</h4>

<p style="margin-bottom:16px;color:#555">
<strong>Score Breakdown:</strong>
</p>

<table style="width:100%;font-size:0.9rem;border:none">
<tr><td style="border:none;padding:8px 0"><strong>Doctor Availability:</strong></td><td style="border:none;padding:8px 0">20 pts (moderate shortage)</td></tr>
<tr><td style="border:none;padding:8px 0"><strong>Neighborhood Health:</strong></td><td style="border:none;padding:8px 0">10 pts (18% chronic disease - near US avg)</td></tr>
<tr><td style="border:none;padding:8px 0"><strong>Air Quality:</strong></td><td style="border:none;padding:8px 0">0 pts (clean air)</td></tr>
<tr><td style="border:none;padding:8px 0"><strong>Disaster Risk:</strong></td><td style="border:none;padding:8px 0">0 pts (low risk)</td></tr>
<tr><td style="border:none;padding:8px 0"><strong>Respiratory Illness:</strong></td><td style="border:none;padding:8px 0">2 pts (minimal activity)</td></tr>
<tr style="border-top:2px solid #ddd"><td style="border:none;padding:12px 0"><strong>Total Score:</strong></td><td style="border:none;padding:12px 0"><strong>35 pts</strong></td></tr>
</table>

<div style="background:#fff3e0;padding:16px;margin-top:20px;border-radius:6px">
<strong>What This Means:</strong>
<ul style="margin:8px 0">
<li>School is in a <strong>moderately healthy area</strong> with some doctor shortage</li>
<li>About 1 in 5 neighbors have chronic disease (close to national average)</li>
<li>Air quality is good, disaster risk is low</li>
<li>Recommended: Standard wellness programs, part-time nurse minimum</li>
</ul>
</div>

</div>

</div>
</details>
</div>
</div>

<div class="charts-grid">
    <div class="chart-card">
        <h3>📊 Schools by County</h3>
        <canvas id="countyChart" style="max-height: 300px"></canvas>
    </div>
    <div class="chart-card">
        <h3>📈 Score Distribution</h3>
        <canvas id="scoreChart" style="max-height: 300px"></canvas>
    </div>
</div>

<table id="schoolTable">
<thead>
<tr>
    <th onclick="sortTable(0)">Rank</th>
    <th onclick="sortTable(1)">School Name</th>
    <th onclick="sortTable(2)">County</th>
    <th onclick="sortTable(3)">Type</th>
    <th onclick="sortTable(4)">Enrollment</th>
    <th onclick="sortTable(5)">Neighborhood Health<br><small>(chronic disease %)</small></th>
    <th onclick="sortTable(6)">Doctor Availability<br><small>(county)</small></th>
    <th onclick="sortTable(7)">Health Need Score<br><small>(0-100)</small></th>
</tr>
</thead>
<tbody>
"""
    
    # Add table rows
    rank = 1
    for _, row in schools_df.iterrows():
        school_name = row["school_name"]
        county = row.get("county", "Unknown")
        school_type = row.get("school_type", "School")
        enrollment = int(row["enrollment"]) if pd.notna(row.get("enrollment")) else "N/A"
        
        chronic = f"{row['chronic_disease_prev']:.1f}" if pd.notna(row.get("chronic_disease_prev")) else '<span class="no-data">No tract data</span>'
        hpsa = f"{int(row['hpsa_primary_care_max'])}" if pd.notna(row.get("hpsa_primary_care_max")) else "-"
        score = row["readiness_score"]
        
        # Score coloring
        score_class = "score-high" if score >= 45 else "score-medium" if score >= 30 else "score-low"
        
        html += f"""<tr>
    <td class="rank">{rank}</td>
    <td class="school-name">{school_name}</td>
    <td><span class="county-badge">{county}</span></td>
    <td>{school_type}</td>
    <td class="enrollment">{enrollment:,}</td>
    <td>{chronic}</td>
    <td>{hpsa}</td>
    <td class="score {score_class}">{score:.1f}</td>
</tr>
"""
        rank += 1
    
    html += """</tbody>
</table>

<footer style="margin-top:48px; padding-top:32px; border-top:2px solid #eee; color:#666">
<p style="font-size:0.9rem"><strong>Data Sources:</strong> CDC, EPA, HRSA, FEMA (all federal public data)</p>
<p style="margin-top:12px; font-size:0.9rem">Last updated: """ + datetime.utcnow().isoformat(timespec="seconds") + """Z | Updates automatically every morning</p>
<p style="margin-top:16px">
<a href="counties.html" style="color:#1976d2; font-weight:600">View County Comparison</a> | 
<a href="../data/school_scorecard.csv" style="color:#1976d2">Download Data (CSV)</a> | 
<a href="https://github.com/scottmadden/jax-health-scorecard" style="color:#666">Technical Details</a>
</p>
</footer>

</div>

<script>
// Search and filter functionality
function filterTable() {
    const searchValue = document.getElementById('searchInput').value.toLowerCase();
    const countyFilter = document.getElementById('countyFilter').value;
    const scoreFilter = document.getElementById('scoreFilter').value;
    
    const table = document.getElementById('schoolTable');
    const rows = table.getElementsByTagName('tr');
    
    let visibleCount = 0;
    
    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        const schoolName = row.cells[1].textContent.toLowerCase();
        const county = row.cells[2].textContent;
        const scoreText = row.cells[7].textContent;
        const score = parseFloat(scoreText);
        
        let showRow = true;
        
        // Search filter
        if (searchValue && !schoolName.includes(searchValue) && 
            !row.cells[2].textContent.toLowerCase().includes(searchValue)) {
            showRow = false;
        }
        
        // County filter
        if (countyFilter && !county.includes(countyFilter)) {
            showRow = false;
        }
        
        // Score filter
        if (scoreFilter === 'high' && score < 45) showRow = false;
        if (scoreFilter === 'medium' && (score < 30 || score >= 45)) showRow = false;
        if (scoreFilter === 'low' && score >= 30) showRow = false;
        
        row.style.display = showRow ? '' : 'none';
        if (showRow) {
            visibleCount++;
            row.cells[0].textContent = visibleCount; // Update rank
        }
    }
}

// Simple sort functionality
let sortOrder = {};
function sortTable(columnIndex) {
    const table = document.getElementById('schoolTable');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    const currentOrder = sortOrder[columnIndex] || 'asc';
    const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
    sortOrder = {}; // Reset other columns
    sortOrder[columnIndex] = newOrder;
    
    rows.sort((a, b) => {
        let aVal = a.cells[columnIndex].textContent;
        let bVal = b.cells[columnIndex].textContent;
        
        // Try numeric comparison
        const aNum = parseFloat(aVal.replace(/[^0-9.-]/g, ''));
        const bNum = parseFloat(bVal.replace(/[^0-9.-]/g, ''));
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return newOrder === 'asc' ? aNum - bNum : bNum - aNum;
        }
        
        // String comparison
        return newOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    });
    
    rows.forEach(row => tbody.appendChild(row));
    
    // Update ranks
    rows.forEach((row, index) => {
        if (row.style.display !== 'none') {
            row.cells[0].textContent = index + 1;
        }
    });
}

// Initialize charts on page load
document.addEventListener('DOMContentLoaded', function() {
    initCharts();
});

function initCharts() {
    // County distribution chart
    const countyCtx = document.getElementById('countyChart');
    if (countyCtx) {
        const countyData = """ + json.dumps(list(county_counts.items())) + """;
        new Chart(countyCtx, {
            type: 'bar',
            data: {
                labels: countyData.map(d => d[0]),
                datasets: [{
                    label: 'Number of Schools',
                    data: countyData.map(d => d[1]),
                    backgroundColor: ['#1976d2', '#388e3c', '#f57c00', '#7b1fa2', '#c2185b'],
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 10 } }
                }
            }
        });
    }
    
    // Score distribution histogram
    const scoreCtx = document.getElementById('scoreChart');
    if (scoreCtx) {
        const table = document.getElementById('schoolTable');
        const rows = Array.from(table.getElementsByTagName('tr')).slice(1);
        const scores = rows.map(row => parseFloat(row.cells[7].textContent));
        
        // Create histogram bins
        const bins = [0, 20, 25, 30, 35, 40, 45, 50];
        const counts = new Array(bins.length - 1).fill(0);
        scores.forEach(score => {
            for (let i = 0; i < bins.length - 1; i++) {
                if (score >= bins[i] && score < bins[i + 1]) {
                    counts[i]++;
                    break;
                }
            }
        });
        
        new Chart(scoreCtx, {
            type: 'bar',
            data: {
                labels: bins.slice(0, -1).map((b, i) => `${b}-${bins[i+1]}`),
                datasets: [{
                    label: 'Number of Schools',
                    data: counts,
                    backgroundColor: '#4CAF50',
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 5 } }
                }
            }
        });
    }
}
</script>
</body>
</html>"""
    
    return html


def write_school_html(schools_df: pd.DataFrame):
    """Write school scorecard HTML to docs/schools.html"""
    html = generate_school_html(schools_df)
    output_path = DOCS / "schools.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"✅ Wrote school HTML to {output_path}")


if __name__ == "__main__":
    # Load school scorecard and generate HTML
    scorecard_path = OUT / "school_scorecard.csv"
    
    if not scorecard_path.exists():
        print("❌ school_scorecard.csv not found. Run schools.py first.")
        exit(1)
    
    print("Generating school-level HTML visualization...")
    schools = pd.read_csv(scorecard_path)
    
    # Sort by readiness score
    schools = schools.sort_values("readiness_score", ascending=False)
    
    write_school_html(schools)
    
    print(f"\n✅ School HTML generated!")
    print(f"   View at: docs/schools.html")
    print(f"   Will be live at: https://scottmadden.github.io/jax-health-scorecard/schools.html")

