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
    margin-top: 24px;
    font-size: 0.95rem;
}}
thead {{position: sticky; top: 0; background: white; z-index: 10; box-shadow: 0 2px 4px rgba(0,0,0,0.05)}}
th, td {{
    border-bottom: 1px solid #e0e0e0;
    padding: 14px 12px;
    text-align: left;
}}
th {{
    background: white;
    font-weight: 600;
    font-size: 0.85rem;
    cursor: pointer;
    user-select: none;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}}
th:hover {{color: #1976d2}}
td {{vertical-align: middle}}

tbody tr {{
    cursor: pointer;
    transition: background 0.15s;
}}
tbody tr:hover {{
    background: #f5f5f5;
}}
tbody tr.expanded {{
    background: #e3f2fd;
}}

.school-details {{
    display: none;
    background: #fafafa;
    padding: 20px;
    border-left: 4px solid #1976d2;
    margin: 0;
}}
.school-details.show {{
    display: block;
}}
.school-details h4 {{
    margin: 0 0 16px 0;
    color: #1976d2;
    font-size: 1.1rem;
}}
.school-details table {{
    margin: 0;
    font-size: 0.9rem;
    background: white;
    border-radius: 4px;
}}
.school-details td {{
    border: none;
    padding: 10px;
}}
.school-details tr:nth-child(even) {{
    background: #f9f9f9;
}}

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

@media (max-width: 768px) {{
    .container {{padding: 16px}}
    h1 {{font-size: 1.8rem}}
    .stats-grid {{grid-template-columns: 1fr 1fr; gap: 12px}}
    .stat-card {{padding: 16px}}
    .stat-card .value {{font-size: 2rem}}
    .charts-grid {{grid-template-columns: 1fr; gap: 16px}}
    .chart-card {{padding: 16px}}
    table {{font-size: 0.85rem}}
    th, td {{padding: 10px 6px}}
    .controls {{flex-direction: column; align-items: stretch}}
    .search-box {{min-width: 100%}}
    th:nth-child(4), td:nth-child(4) {{display: none}} /* Hide Type column on mobile */
    th:nth-child(5), td:nth-child(5) {{display: none}} /* Hide Enrollment on mobile */
}}

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

<p style="text-align:center;color:#999;font-size:0.95rem;margin:24px 0">
Click any school to see its specific health breakdown
</p>
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
    
    # Add table rows with school-specific details
    rank = 1
    for idx, row in schools_df.iterrows():
        school_name = row["school_name"]
        county = row.get("county", "Unknown")
        school_type = row.get("school_type", "School")
        enrollment = int(row["enrollment"]) if pd.notna(row.get("enrollment")) else "N/A"
        
        chronic = f"{row['chronic_disease_prev']:.1f}" if pd.notna(row.get("chronic_disease_prev")) else '<span class="no-data">No data</span>'
        chronic_val = row.get("chronic_disease_prev", 0)
        hpsa = f"{int(row['hpsa_primary_care_max'])}" if pd.notna(row.get("hpsa_primary_care_max")) else "-"
        hpsa_val = row.get("hpsa_primary_care_max", 0)
        score = row["readiness_score"]
        
        # Get individual scores
        score_chronic = row.get("score_chronic", 0)
        score_hpsa = row.get("score_hpsa", 0)
        score_air = row.get("score_air_q", 0)
        score_hazard = row.get("score_hazard", 0)
        score_resp = row.get("score_respiratory", 0)
        resp_activity = row.get("respiratory_activity", "Unknown")
        
        # Score coloring
        score_class = "score-high" if score >= 45 else "score-medium" if score >= 30 else "score-low"
        need_level = "High Need" if score >= 45 else "Medium Need" if score >= 30 else "Low Need"
        
        html += f"""<tr onclick="toggleDetails(this, {idx})">
    <td class="rank">{rank}</td>
    <td class="school-name">{school_name}</td>
    <td><span class="county-badge">{county}</span></td>
    <td>{school_type}</td>
    <td class="enrollment">{enrollment if isinstance(enrollment, str) else f'{enrollment:,}'}</td>
    <td>{chronic}</td>
    <td>{hpsa}</td>
    <td class="score {score_class}">{score:.1f}</td>
</tr>
<tr class="detail-row" id="details-{idx}" style="display:none">
    <td colspan="8" style="padding:0">
        <div class="school-details">
            <h4>{school_name} - Detailed Breakdown</h4>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:20px">
                <div>
                    <table style="width:100%;margin:0">
                        <tr><td style="font-weight:600;color:#555">Overall Score:</td><td style="font-weight:700;color:{('#d32f2f' if score >= 45 else '#f57c00' if score >= 30 else '#2e7d32')}">{score:.1f} pts ({need_level})</td></tr>
                        <tr><td>County:</td><td>{county}</td></tr>
                        <tr><td>Type:</td><td>{school_type}</td></tr>
                        <tr><td>Enrollment:</td><td>{enrollment if isinstance(enrollment, str) else f'{enrollment:,}'} students</td></tr>
                    </table>
                </div>
                <div>
                    <table style="width:100%;margin:0">
                        <tr style="background:#f0f0f0"><td colspan="2" style="font-weight:600;padding:8px">Score Components:</td></tr>
                        <tr><td>Neighborhood Health:</td><td><strong>{score_chronic:.1f} pts</strong> ({chronic_val:.1f}% chronic disease)</td></tr>
                        <tr><td>Doctor Availability:</td><td><strong>{score_hpsa:.1f} pts</strong> (shortage score: {hpsa_val if pd.notna(hpsa_val) else 'N/A'})</td></tr>
                        <tr><td>Air Quality:</td><td><strong>{score_air:.1f} pts</strong></td></tr>
                        <tr><td>Disaster Risk:</td><td><strong>{score_hazard:.1f} pts</strong></td></tr>
                        <tr><td>Respiratory Illness:</td><td><strong>{score_resp:.1f} pts</strong> ({resp_activity})</td></tr>
                    </table>
                </div>
            </div>
            <p style="margin-top:16px;font-size:0.9rem;color:#666">Click row again to collapse</p>
        </div>
    </td>
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
// Toggle school-specific details
function toggleDetails(rowElement, schoolId) {
    const detailRow = document.getElementById('details-' + schoolId);
    const isVisible = detailRow.style.display !== 'none';
    
    // Close all other detail rows
    document.querySelectorAll('.detail-row').forEach(row => {
        row.style.display = 'none';
    });
    document.querySelectorAll('tbody tr').forEach(row => {
        row.classList.remove('expanded');
    });
    
    // Toggle this one
    if (!isVisible) {
        detailRow.style.display = 'table-row';
        rowElement.classList.add('expanded');
    }
}

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

