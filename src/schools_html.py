#!/usr/bin/env python3
"""
Phase 4: School-Level HTML Visualization Generator
Creates interactive, searchable school health readiness table.
"""
import pandas as pd
import pathlib
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
    
    title = "Jacksonville-Area School Health Readiness Scorecard (Phase 4)"
    
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* {{box-sizing: border-box}}
body {{
    font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background: #f5f5f5;
}}
.container {{max-width: 1400px; margin: 0 auto; background: white; padding: 24px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1)}}
h1 {{margin: 0; font-size: 2rem; color: #1a1a1a}}
.badge {{display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 0.75rem; background: #7c4dff; color: white; margin-left: 12px; font-weight: 600}}
h2 {{margin: 12px 0; color: #666; font-weight: 500; font-size: 1.1rem}}

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

<h1>{title} <span class="badge">PHASE 4</span></h1>
<h2>Individual school rankings with tract-level health data</h2>

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
<h3>📊 Scoring System (100 Points Total)</h3>
<ul>
<li><strong>Primary Care Access (30 pts):</strong> County-level HRSA HPSA shortage score</li>
<li><strong>Chronic Disease (30 pts):</strong> Tract-level CDC PLACES prevalence (diabetes, obesity, asthma)</li>
<li><strong>Air Quality (15 pts):</strong> County-level EPA/AirNow data</li>
<li><strong>Hazard Risk (15 pts):</strong> County-level FEMA National Risk Index</li>
<li><strong>Respiratory Virus (10 pts):</strong> State-level CDC flu/COVID/RSV activity</li>
</ul>
<p style="margin: 12px 0 0 0; color: #666; font-size: 0.9rem;">
<strong>Higher score = higher health risk/need.</strong> Schools without tract data use county averages.
</p>
</div>

<div class="controls">
    <div class="search-box">
        <input type="text" id="searchInput" placeholder="🔍 Search schools by name, city, or district..." onkeyup="filterTable()">
    </div>
    <div class="filter-group">
        <label for="countyFilter">County:</label>
        <select id="countyFilter" onchange="filterTable()">
            <option value="">All Counties</option>
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

<table id="schoolTable">
<thead>
<tr>
    <th onclick="sortTable(0)">Rank</th>
    <th onclick="sortTable(1)">School Name</th>
    <th onclick="sortTable(2)">County</th>
    <th onclick="sortTable(3)">Type</th>
    <th onclick="sortTable(4)">Enrollment</th>
    <th onclick="sortTable(5)">Chronic Disease (%)</th>
    <th onclick="sortTable(6)">HPSA Score</th>
    <th onclick="sortTable(7)">Readiness Score</th>
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

<footer>
<p><strong>Data Sources:</strong> CDC PLACES (tract-level), HRSA HPSA, EPA AirData, FEMA NRI, CDC Respiratory Surveillance</p>
<p><strong>Last Updated:</strong> """ + datetime.utcnow().isoformat(timespec="seconds") + """Z | Auto-refreshes daily at 9:15am ET</p>
<p><strong>View:</strong> <a href="index.html">County Scorecard</a> | <a href="https://github.com/scottmadden/jax-health-scorecard">GitHub Repository</a> | <a href="../data/school_scorecard.csv">Download CSV</a></p>
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

